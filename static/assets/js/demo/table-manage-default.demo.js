/*
Template Name: Color Admin - Responsive Admin Dashboard Template build with Twitter Bootstrap 3 & 4
Version: 4.0.0
Author: Sean Ngu
Website: http://www.seantheme.com/color-admin-v4.0/admin/
*/

var handleDataTableDefault = function() {
	"use strict";
    
    if ($('#data-table-default').length !== 0) {
        $('#data-table-default').DataTable({
            responsive: true
        });
    }
    
    if ($('#tableListUser').length !== 0) {
        $('#tableListUser').DataTable({
            responsive: true,
            searching: false,
            lengthChange: false,
            pageLength: 10,
            destroy: true,
            language: {
                info: "Mostrando _START_ a _END_ de _TOTAL_ registros",
                paginate: {
                    first: "Primero",
                    last: "Último",
                    next: "Siguiente",
                    previous: "Anterior"
                },
            },

        });
    }

};


var TableManageDefault = function () {
	"use strict";
    return {
        //main function
        init: function () {
            handleDataTableDefault();
        }
    };
}();