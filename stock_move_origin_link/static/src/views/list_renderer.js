/** @odoo-module **/

import { ListRenderer } from "@web/views/list/list_renderer";
import { patch } from '@web/core/utils/patch';


patch(ListRenderer.prototype, 'stock_move_origin_link_list_renderer', {
    /**
     * @override
     */
    hasOriginFields(record) {
        const validModels = ["stock.picking", "stock.move", "stock.move.line"];
        return validModels.includes(record.resModel);
    }
});