/*
  © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
  License LGPL-3.0 or later (http://www.gnu.org/licenses/LGPL.html).
*/
odoo.define("stock_move_origin_link", function(require) {
"use strict";

var rpc = require("web.rpc");
var Class = require("web.Class");

var stockMoveModels = ["stock.move", "stock.move.line", "stock.picking"];

var AccessVerifier = Class.extend({
    init(){
        this._accessCache = new Map();
    },
    /**
     * Check whether a given model is readable by the user.
     *
     * @param {String} model - the model to search
     * @returns {Boolean} true if the model is readable by the user, false otherwise.
     */
    async isModelReadable(model){
        if(odoo.session_info.is_superuser){
            return true;
        }
        if(!this._accessCache.has(model)){
            var result = await rpc.query({
                model,
                method: "check_access_rights",
                kwargs: {operation: "read", raise_exception: false}
            });
            this._accessCache.set(model, result);
        }
        return this._accessCache.get(model);
    },
})
var accessVerifier = new AccessVerifier();

function isModuleInstalled(moduleName){
    return odoo._modules.indexOf(moduleName) !== -1;
}

/**
 * Search related documents from the given origins.
 *
 * @param {String} model - the model of document to search
 * @param {String} module - the module that adds the given model
 * @param {Array} origins - the origins to search
 * @returns {Map} a mapping of document names from origins
 */
async function searchDocumentsFromOrigins(model, module_, origins){
    if(!isModuleInstalled(module_)){
        return new Map();
    }

    var isModelReadable = await accessVerifier.isModelReadable(model);
    if(!isModelReadable){
        return new Map();
    }

    var domain = [["name", "in", origins]];
    var data = await rpc.query({model, method: "search_read", args: [domain, ["name"]]});
    var recordMapping = new Map();
    data.forEach((document_) => {
        document_.model = model;
        recordMapping.set(document_.name, document_);
    });
    return recordMapping;
}

require("web.ListRenderer").include({
    _renderView(){
        if(stockMoveModels.indexOf(this.state.model) !== -1){
            var super_ = this._super;
            var self = this;
            var args = arguments;
            return this._setUpStockMoveOriginLinks().then(() => {
                return super_.apply(self, args);
            });
        }
        return this._super();
    },
    /**
     * Prepare the data relevant for displaying links in the list view.
     *
     * The relevant data is a mapping of PO / SO / MO that match any origin document name
     * mentionned on any row.
     */
    async _setUpStockMoveOriginLinks(){
        var origins = new Set(this.state.data.map((row) => row.data.origin));
        origins.delete(false);
        origins = Array.from(origins);
        this._purchaseOrderOriginMapping = await searchDocumentsFromOrigins("purchase.order", "purchase", origins);
        this._saleOrderOriginMapping = await searchDocumentsFromOrigins("sale.order", "sale", origins);
        this._manufacturingOrderOriginMapping = await searchDocumentsFromOrigins("mrp.production", "mrp", origins);
    },
    /**
     * Display the link on the origin field for every rows.
     */
    _renderBodyCell(record, node, colIndex, options){
        var td = this._super.apply(this, arguments);
        if(
            stockMoveModels.indexOf(this.state.model) !== -1 &&
            node.tag === "field" &&
            node.attrs.name === "origin"
        ){
            this._addStockMoveOriginLinkToBodyCell(record, td);
        }
        return td;
    },
    /**
     * Get the origin document related to the given record.
     *
     * The origin is a text value given in the field `origin`.
     * It can refer to a PO, a SO, a MO, or something else.
     *
     * When this method is called, the origin documents have already been
     * searched from the server.
     *
     * @param {Object} record - the current record
     * @returns {Object} - the origin record
     */
    _getStockMoveRelatedObject(record){
        var origin = record.data.origin;
        if(!origin){
            return null;
        }
        if(this._purchaseOrderOriginMapping.has(origin)){
            return this._purchaseOrderOriginMapping.get(origin);
        }
        if(this._saleOrderOriginMapping.has(origin)){
            return this._saleOrderOriginMapping.get(origin);
        }
        if(this._manufacturingOrderOriginMapping.has(origin)){
            return this._manufacturingOrderOriginMapping.get(origin);
        }
        return null;
    },
    /**
     * Add the link to the form view of the origin document to the cell.
     *
     * @param {Object} record - the record related to the view row.
     * @param {JQueryElement} td - the table cell on which to display the link.
     */
    _addStockMoveOriginLinkToBodyCell(record, td){
        var relatedObject = this._getStockMoveRelatedObject(record);
        if(!relatedObject){
            return;
        }
        var tdContent = td.contents();
        var link = $("<a></a>")
        link.attr("href", _.str.sprintf("#id=%s&model=%s", relatedObject.id, relatedObject.model));
        link.append(tdContent);
        link.click(async (event) => {
            event.preventDefault();
            event.stopPropagation();
            var action = await this._rpc({
                model: relatedObject.model,
                method: "get_formview_action",
                args: [[relatedObject.id]],
            });
            this.trigger_up("do_action", {action: action});
        });
        td.empty().append(link);
    },
});

});
