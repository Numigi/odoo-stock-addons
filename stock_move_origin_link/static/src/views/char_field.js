/** @odoo-module **/

import { CharField } from "@web/views/fields/char/char_field";
import { patch } from '@web/core/utils/patch';
import rpc from "web.rpc";

const validModels = ["stock.picking", "stock.move", "stock.move.line"];


patch(CharField.prototype, 'stock_move_origin_link_charfield', {

    setup() {
        this.props.isOrigin = this.hasOriginFields();
        this.props.OriginUrl = true; // Force to false , for the tests
        this._super(...arguments);
    },


    hasOriginFields() {
        var res = this.props.name === 'origin' && validModels.includes(this.props.record.resModel);
        return res;
    },


    async getRecordFormViewAction(record) {
        return await rpc.query({
            model: record.model,
            method: "get_formview_action",
            args: [[record.id]]
        });
    },

    async isModuleInstalled(moduleName) {
        const domains = [["name", "=", moduleName], ["state", "=", "installed"]];
        const res = await rpc.query({
            model: "ir.module.module",
            method: "search_read",
            args: [domains],
        });
        return res.length === 0 ? null : res;
    },

    async searchDocumentsFromOrigins(model, module_, record) {

        const installedModules = await this.isModuleInstalled(module_);
        if (installedModules === null) {
            return false;
        }

        const domain = [["name", "=", record.data.origin]];
        const data = await rpc.query({
            model,
            method: "search_read",
            args: [domain, ["name"]]
        });

        return data.length === 0 ? false : { ...data[0], model: model };
    },

    _getStockMoveOriginRecord() {
        if (this._purchaseOrderOriginMapping) {
            return this._purchaseOrderOriginMapping;
        }
        if (this._saleOrderOriginMapping) {
            return this._saleOrderOriginMapping;
        }
        if (this._manufacturingOrderOriginMapping) {
            return this._manufacturingOrderOriginMapping;
        }
        return null;
    },

    async prepareUrlOrigins(record) {
        const origin = record.data.origin;

        if (!origin) {
            return false;
        }

        this._purchaseOrderOriginMapping = await this.searchDocumentsFromOrigins("purchase.order", "purchase", record);
        this._saleOrderOriginMapping = await this.searchDocumentsFromOrigins("sale.order", "sale", record);
        this._manufacturingOrderOriginMapping = await this.searchDocumentsFromOrigins("mrp.production", "mrp", record);

        const result = this._getStockMoveOriginRecord();

        if (result) {
            return result;
        }
        return false;
    },

    async getUrlOrigins(record) {
        var url = await this.prepareUrlOrigins(record);
        return url;
    }
});
CharField.props = {
    ...CharField.props,
    isOrigin: { type: Boolean, optional: true },
    OriginUrl: { type: Boolean, optional: true },
};

