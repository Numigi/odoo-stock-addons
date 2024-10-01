/** @odoo-module **/

import { CharField } from "@web/views/fields/char/char_field";
import { patch } from '@web/core/utils/patch';
import { useService } from "@web/core/utils/hooks";
import { onWillStart, onMounted, onWillUpdateProps, Component } from "@odoo/owl";
import rpc from "web.rpc";

const VALID_MODELS = ["stock.picking", "stock.move", "stock.move.line"];

// AccessVerifier Class for caching access checks
class AccessVerifier extends Component {
    constructor() {
        super(...arguments);
        this._accessCache = new Map();
    }

    // Check if the model is readable, with caching
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

// Global instance of AccessVerifier
const accessVerifier = new AccessVerifier();
const originCache = new Map();

// Patch CharField prototype
patch(CharField.prototype, 'stock_move_origin_link_charfield', {
    setup() {
        this.props.hasOrigin = this.hasOriginField();
        this.actionService = useService("action");
        this._super(...arguments);

        // Setup hooks
        onWillStart(this.updateOriginIfNeeded.bind(this));
        onWillUpdateProps(this.handleUpdateProps.bind(this));
        onMounted(this.updateOriginIfNeeded.bind(this));
    },

    // Consolidate origin update logic
    async updateOriginIfNeeded() {
        if (!this.props.originUrl && this.props.hasOrigin) {
            await this.updateOriginUrl(this.props.record);
        }
    },

    async handleUpdateProps(nextProps) {
        if (nextProps.record !== this.props.record && !nextProps.originUrl && this.props.hasOrigin) {
            await this.updateOriginUrl(nextProps.record);
        }
    },

    async updateOriginUrl(record) {
        try {
            if (originCache.has(record.id)) {
                const cachedOrigin = originCache.get(record.id);
                this.props.originRecord = cachedOrigin.record;
                this.props.originUrl = cachedOrigin.url;
                return;
            }

            if (this.hasOriginField()) {
                const originRecord = await this.computeOriginUrl(record);
                const originUrl = originRecord ? `#id=${originRecord.id}&model=${originRecord.model}` : null;
                this.props.originRecord = originRecord;
                this.props.originUrl = originUrl;

                if (originRecord) {
                    originCache.set(record.id, { record: originRecord, url: originUrl });
                }
            }
        } catch (error) {
            this.handleError('Failed to update origin URL:', error);
        }
    },

    // Check if the field has an origin
    hasOriginField() {
        return this.props.name === 'origin' && VALID_MODELS.includes(this.props.record.resModel) && this.props.record.data.origin;
    },

    // Fetch the form view action
    async getRecordFormViewAction(record) {
        try {
            return await rpc.query({
                model: record.model,
                method: "get_formview_action",
                args: [[record.id]],
            });
        } catch (error) {
            this.handleError('Error fetching form view action:', error);
            return null;
        }
    },

    // Handle link click event
    async onLinkClick(event) {
        event.preventDefault();
        event.stopPropagation();

        if (this.props.originRecord) {
            const action = await this.getRecordFormViewAction(this.props.originRecord);
            this.actionService.doAction(action);
        }
    },

    // Check if a module is installed, with caching
    async isModuleInstalled(moduleName) {
        try {
            const result = await rpc.query({
                model: "ir.module.module",
                method: "search_read",
                args: [[["name", "=", moduleName], ["state", "=", "installed"]]],
            });
            return result.length > 0;
        } catch (error) {
            this.handleError(`Error checking if module ${moduleName} is installed:`, error);
            return false;
        }
    },

    // Fetch documents based on origin field
    async fetchDocumentsByOrigin(modelName, moduleName, record) {
        try {
            if (!(await this.isModuleInstalled(moduleName))) {
                return false;
            }

            if (!(await accessVerifier.isModelReadable(modelName))) {
                return false;
            }

            const data = await rpc.query({
                model: modelName,
                method: "search_read",
                args: [[["name", "=", record.data.origin]], ["name"]],
            });

            return data.length ? { ...data[0], model: modelName } : false;

        } catch (error) {
            this.handleError(`Error fetching documents for model ${modelName}:`, error);
            return false;
        }
    },

    // Compute origin URL by checking various models
    async computeOriginUrl(record) {
        try {
            return (
                await this.fetchDocumentsByOrigin("purchase.order", "purchase", record) ||
                await this.fetchDocumentsByOrigin("sale.order", "sale", record) ||
                await this.fetchDocumentsByOrigin("mrp.production", "mrp", record) ||
                null
            );
        } catch (error) {
            this.handleError('Error computing origin URL:', error);
            return null;
        }
    },

    // Error handling helper
    handleError(message, error) {
        console.error(message, error);
        this.props.originUrl = null;
        this.props.originRecord = null;
    }
});

// Extend CharField props
CharField.props = {
    ...CharField.props,
    hasOrigin: { type: Boolean, optional: true },
    originUrl: { type: String, optional: true },
    originRecord: { type: Object, optional: true },
};
