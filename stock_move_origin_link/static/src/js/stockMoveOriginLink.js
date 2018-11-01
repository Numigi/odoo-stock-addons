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
});

var accessVerifier = new AccessVerifier();

var OriginDocumentCache = Class.extend({
    init(){
        this._cache = new Map();
    },
    getOriginDocumentMapping(originType){
        if(!this._cache.has(originType)){
            this._cache.set(originType, new Map());
        }
        return this._cache.get(originType);
    },
});

var originDocumentCache = new OriginDocumentCache();

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

    var recordMapping = originDocumentCache.getOriginDocumentMapping(model);

    var missingOrigins = origins.filter((o) => !recordMapping.has(o));
    if(missingOrigins.length){
        var domain = [["name", "in", origins]];
        var data = await rpc.query({model, method: "search_read", args: [domain, ["name"]]});
        data.forEach((document_) => {
            document_.model = model;
            recordMapping.set(document_.name, document_);
        });
        missingOrigins.forEach((origin) => {
            if(!recordMapping.has(origin)){
                recordMapping.set(origin, null);
            }
        });
    }

    return recordMapping;
}


async function getRecordFormViewAction(record){
    return await rpc.query({model: record.model, method: "get_formview_action", args: [[record.id]]});
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
    _getStockMoveOriginRecord(record){
        var origin = record.data.origin;
        if(!origin){
            return null;
        }
        if(this._purchaseOrderOriginMapping.get(origin)){
            return this._purchaseOrderOriginMapping.get(origin);
        }
        if(this._saleOrderOriginMapping.get(origin)){
            return this._saleOrderOriginMapping.get(origin);
        }
        if(this._manufacturingOrderOriginMapping.get(origin)){
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
        var originRecord = this._getStockMoveOriginRecord(record);
        if(!originRecord){
            return;
        }
        var tdContent = td.contents();
        var link = $("<a></a>");
        link.attr("href", _.str.sprintf("#id=%s&model=%s", originRecord.id, originRecord.model));
        link.append(tdContent);
        link.click(async (event) => {
            event.preventDefault();
            event.stopPropagation();
            var action = await getRecordFormViewAction(originRecord);
            this.trigger_up("do_action", {action});
        });
        td.empty().append(link);
    },
});

require("web.FormRenderer").include({
    _renderView() {
        var result = this._super.apply(this, arguments);
        if(
            stockMoveModels.indexOf(this.state.model) !== -1 &&
            this.mode === "readonly"
        ){
            var originFieldWidget = this.allFieldWidgets[this.state.id].filter((w) => w.name === "origin")[0];
            if(originFieldWidget){
                this._addStockMoveOriginLinkToFieldNode(originFieldWidget);
            }
        }
        return result;
    },
    async _addStockMoveOriginLinkToFieldNode(originFieldWidget){
        var originRecord = await this._searchStockMoveOriginRecord();
        if(!originRecord){
            return;
        }
        var widgetContent = originFieldWidget.$el.contents();
        var link = $("<a></a>");
        link.attr("href", _.str.sprintf("#id=%s&model=%s", originRecord.id, originRecord.model));
        link.append(widgetContent);
        link.click(async (event) => {
            event.preventDefault();
            event.stopPropagation();
            var action = await getRecordFormViewAction(originRecord);
            this.trigger_up("do_action", {action});
        });
        originFieldWidget.$el.empty().append(link);
    },
    /**
     * Search the origin document related to the form record.
     *
     * In a form view, the related documents does not need to be cached,
     * because only one origin field is rendered.
     *
     * @returns {Object} - the origin record
     */
    async _searchStockMoveOriginRecord(){
        var origin = this.state.data.origin;
        if(!origin){
            return null;
        }
        var poMapping = await searchDocumentsFromOrigins("purchase.order", "purchase", [origin]);
        if(poMapping.get(origin)){
            return poMapping.get(origin);
        }
        var soMapping = await searchDocumentsFromOrigins("sale.order", "sale", [origin]);
        if(soMapping.get(origin)){
            return soMapping.get(origin);
        }
        var moMapping = await searchDocumentsFromOrigins("mrp.production", "mrp", [origin]);
        if(moMapping.get(origin)){
            return moMapping.get(origin);
        }
        return null;
    },
});

});
