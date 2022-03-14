odoo.define('dealba_custom.proyecto_avance', function (require){
    "use strict";

    var AbstractAction = require("web.AbstractAction");
    var core = require("web.core");
    var ReportWidget = require("web.Widget");

    var proyecto_avance = AbstractAction.extend({
        hasControlPanel: true,

        init: function (parent, action) {
            this._super.apply(this, arguments);
            this.odoo_context = action.context;
        },

        willStart: function () {
            return Promise.all([this._super.apply(this, arguments), this.get_html()]);
        },

        set_html: function () {
            var self = this;
            var def = Promise.resolve();
            if (!this.report_widget) {
                this.report_widget = new ReportWidget(this, this.given_context);
                def = this.report_widget.appendTo(this.$(".o_content"));
            }
            def.then(function () {
                self.report_widget.$el.html(self.html);
            });
        },

        start: function () {
            var self = this;
            this._super();
            this.set_html();
            setTimeout(function() {
                self.canvas_hito_donuts();
                self.canvas_hito_bar();
                self.canvas_fases();
                self.canvas_avance_proyecto();
            }, 100)
        },

        get_html: function () {
            var self = this;
            var defs = [];

            return this._rpc({
                model: "project.project",
                method: "get_html",
                args: [self.odoo_context],
                context: self.odoo_context,
            }).then(function (result) {
                self.html = result.html;
                defs.push(self.update_cp());
                return $.when.apply($, defs);
            });
        },

        update_cp: function () {
            if (this.$buttons) {
                var status = {
                    breadcrumbs: this.actionManager.get_breadcrumbs(),
                    cp_content: {$buttons: this.$buttons},
                };
                return this.update_control_panel(status);
            }
        },

        do_show: function () {
            this._super();
            this.update_cp();
        },

        canvas_hito_donuts: function() {
            var self = this
            var ctx = document.getElementById('canvas_hito_donuts');
            this._rpc({
                model: "project.project",
                method: "canvas_hito_donuts",
                args: [self.odoo_context.active_id],
                context: self.odoo_context,
            }).then(function (result) {
                var data = {
                    labels: result[0],
                    datasets: [
                        {
                            label: "",
                            data: result[1],
                            backgroundColor: [
                                "rgb(76, 143, 252)",
                                "rgb(149, 76, 252)"
                            ],
                        },
                    ]
                };
                var options = {
                    responsive: true,
                    title: {
                        display: true,
                        position: "top",
                        text: "% de Avance",
                        fontSize: 18,
                        fontColor: "#111"
                    },
                    legend: {
                        display: true,
                        position: "bottom",
                        labels: {
                            fontColor: "#333",
                            fontSize: 11
                        }
                    },
                };
                var chart = new Chart(ctx, {
                    type: "doughnut",
                    data: data,
                    options: options,
                });
            });
        },

        canvas_hito_bar: function() {
            var self = this
            var ctx = document.getElementById('canvas_hito_bar');
            this._rpc({
                model: "project.project",
                method: "canvas_hito_bar",
                args: [self.odoo_context.active_id],
                context: self.odoo_context,
            }).then(function (arrays) {
                var data = {
                    labels: arrays[0],
                    datasets: [
                        {
                            label: "Avance",
                            data: arrays[1],
                            backgroundColor: [
                                "rgb(76, 143, 252)",
                                "rgb(149, 76, 252)"
                            ],
                        },

                    ]
                };
                var options = {
                    responsive: true,
                    title: {
                        display: true,
                        position: "top",
                        text: "Avance de hitos",
                        fontSize: 18,
                        fontColor: "#111"
                    },
                    legend: {
                        display: false,
                        position: "bottom",
                        labels: {
                            fontColor: "#333",
                            fontSize: 11
                        }
                    },
                    scales: {
                        xAxes: [{
                            ticks: {
                                suggestedMin: 0,
                                suggestedMax: 100
                            }
                        }]
                    },
                };
                var chart = new Chart(ctx, {
                    type: "horizontalBar",
                    data: data,
                    options: options
                });
            });
        },

        canvas_fases: function() {
            var self = this;
            var i = 0;
            var canvas;
            var key;
            this._rpc({
                model: "project.project",
                method: "contar_fases",
                args: [self.odoo_context.active_id],
                context: self.odoo_context,
            }).then(function (ctd_fases) {
                for(i = 1; i <= ctd_fases; i++) {
                    canvas = "canvas_fase_" + i;
                    window['ctx_' + i] = document.getElementById(canvas);
                }
                self._rpc({
                    model: "project.project",
                    method: "data_fases",
                    args: [self.odoo_context.active_id],
                    context: self.odoo_context,
                }).then(function (data_fases) {
                    i = 1;
                    for(key in data_fases) {
                        if(data_fases.hasOwnProperty(key)) {
                            var data = {
                                labels: data_fases[key][0],
                                datasets: [
                                    {
                                        label: "Avance",
                                        data: data_fases[key][1],
                                        backgroundColor: [
                                            "rgb(227, 54, 54)",
                                            "rgb(76, 143, 252)",
                                            "rgb(149, 76, 252)"
                                        ],
                                    },
                                ]
                            };
                            var options = {
                                responsive: true,
                                title: {
                                    display: true,
                                    position: "top",
                                    text: "Fase " + i,
                                    fontSize: 18,
                                    fontColor: "#111"
                                },
                                legend: {
                                    display: false,
                                    position: "bottom",
                                    labels: {
                                        fontColor: "#333",
                                        fontSize: 11
                                    }
                                },
                                scales: {
                                    xAxes: [{
                                        ticks: {
                                            suggestedMin: 0,
                                            suggestedMax: 100
                                        }
                                    }]
                                },
                            };
                            var chart = new Chart(eval(key), {
                                type: "horizontalBar",
                                data: data,
                                options: options
                            });
                        }
                        i += 1;
                    }
                });
            });
        },

        canvas_avance_proyecto: function() {
            var self = this
            var ctx = document.getElementById('canvas_avance_proyecto');
            this._rpc({
                model: "project.project",
                method: "canvas_avance_proyecto",
                args: [self.odoo_context.active_id],
                context: self.odoo_context,
            }).then(function (arrays) {
                var data = {
                    labels: arrays[0],
                    datasets: [
                        {
                            label: "Avance",
                            data: arrays[1],
                            backgroundColor: [
                                "rgb(76, 143, 252)",
                                "rgb(149, 76, 252)"
                            ],
                        },
                    ]
                };
                var options = {
                    responsive: true,
                    title: {
                        display: true,
                        position: "top",
                        text: "Avance de proyecto",
                        fontSize: 18,
                        fontColor: "#111"
                    },
                    legend: {
                        display: false,
                        position: "bottom",
                        labels: {
                            fontColor: "#333",
                            fontSize: 11
                        }
                    },
                    scales: {
                        xAxes: [{
                            ticks: {
                                suggestedMin: 0,
                                suggestedMax: 100
                            }
                        }]
                    },
                };

                var chart = new Chart(ctx, {
                    type: "horizontalBar",
                    data: data,
                    options: options
                });
            });
        },

    });

    core.action_registry.add("proyecto_avance", proyecto_avance);
    return proyecto_avance;

})