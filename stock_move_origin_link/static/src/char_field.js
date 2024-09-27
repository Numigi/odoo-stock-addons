/** @odoo-module **/

import { CharField } from "@web/views/fields/char/char_field";
import { patch } from '@web/core/utils/patch';
import { useService } from "@web/core/utils/hooks";
import { onWillStart, onMounted, onWillUpdateProps, Component } from "@odoo/owl";
import rpc from "web.rpc";

const VALID_MODELS = ["stock.picking", "stock.move", "stock.move.line"];

class AccessVerifier extends Component {
    constructor() {
        super(...arguments);
        this._accessCache = new Map();
    }

    async isModelReadable(model) {

        if (!this._accessCache.has(model)) {
            const result = await rpc.query({
                model: model,
                method: "check_access_rights",
                kwargs: { operation: "read", raise_exception: false }
            });
            this._accessCache.set(model, result);
        }
        return this._accessCache.get(model);
    }
}

const accessVerifier = new AccessVerifier();
const originCache = new Map();

patch(CharField.prototype, 'stock_move_origin_link_charfield', {
    setup() {
        this.props.hasOrigin = this.hasOriginField();
        this.actionService = useService("action");
        this._super(...arguments);

        onWillStart(async () => {
            if (!this.props.originUrl && this.props.hasOrigin) {
                await this.updateOriginUrl(this.props.record);
            }
        });

        onWillUpdateProps(async (nextProps) => {
            if (nextProps.record !== this.props.record && !nextProps.originUrl && this.props.hasOrigin) {
                await this.updateOriginUrl(nextProps.record);
            }
        });

        onMounted(async () => {
            if (!this.props.originUrl && this.props.hasOrigin) {
                await this.updateOriginUrl(this.props.record);
            }
        });
    },

    async updateOriginUrl(record) {
        try {
            if (!this.props.originUrl && originCache.has(record.id)) {
                const cachedOrigin = originCache.get(record.id);
                this.props.originRecord = cachedOrigin.record;
                this.props.originUrl = cachedOrigin.url;
            } else if (!this.props.originUrl) {
                this.props.hasOrigin = this.hasOriginField();
                const originRecord = await this.computeOriginUrl(record);
                const originUrl = originRecord ? `#id=${originRecord.id}&model=${originRecord.model}` : null;
                this.props.originRecord = originRecord;
                this.props.originUrl = originUrl;
                if (originRecord) {
                    originCache.set(record.id, { record: originRecord, url: originUrl });
                }
            }
        } catch (error) {
            console.error('Failed to update origin URL:', error);
            this.props.originUrl = null;
            this.props.originRecord = null;
        }
    },

    hasOriginField() {
        return this.props.name === 'origin' && VALID_MODELS.includes(this.props.record.resModel);
    },

    async getRecordFormViewAction(record) {
        try {
            return await rpc.query({
                model: record.model,
                method: "get_formview_action",
                args: [[record.id]],
            });
        } catch (error) {
            console.error('Error fetching form view action:', error);
            return null;
        }
    },

    async onLinkClick(event) {
        event.preventDefault();
        event.stopPropagation();

        try {
            const originRecord = this.props.originRecord;
            if (originRecord) {
                const action = await this.getRecordFormViewAction(originRecord);
                this.actionService.doAction(action);

            }
        } catch (error) {
            console.error('Error handling link click:', error);
        }
    },

    async isModuleInstalled(moduleName) {
        try {
            const result = await rpc.query({
                model: "ir.module.module",
                method: "search_read",
                args: [[["name", "=", moduleName], ["state", "=", "installed"]]],
            });
            return result.length > 0 ? result : null;
        } catch (error) {
            console.error(`Error checking if module ${moduleName} is installed:`, error);
            return null;
        }
    },

    async fetchDocumentsByOrigin(modelName, moduleName, record) {
        try {
            const installedModules = await this.isModuleInstalled(moduleName);
            if (!installedModules) {
                return false;
            }
            const isReadable = await accessVerifier.isModelReadable(modelName);
            if (!isReadable) {
                return false;
            }

            const data = await rpc.query({
                model: modelName,
                method: "search_read",
                args: [[["name", "=", record.data.origin]], ["name"]],
            });
            return data.length ? { ...data[0], model: modelName } : false;

        } catch (error) {
            console.error(`Error fetching documents for model ${modelName}:`, error);
            return false;
        }
    },

    async computeOriginUrl(record) {
        try {
            const purchaseOrder = await this.fetchDocumentsByOrigin("purchase.order", "purchase", record);
            if (purchaseOrder) return purchaseOrder;

            const saleOrder = await this.fetchDocumentsByOrigin("sale.order", "sale", record);
            if (saleOrder) return saleOrder;

            const mrpProduction = await this.fetchDocumentsByOrigin("mrp.production", "mrp", record);
            return mrpProduction || null;

        } catch (error) {
            console.error('Error computing origin URL:', error);
            return null;
        }
    }
});

CharField.props = {
    ...CharField.props,
    hasOrigin: { type: Boolean, optional: true },
    originUrl: { type: String, optional: true },
    originRecord: { type: Object, optional: true }
};
