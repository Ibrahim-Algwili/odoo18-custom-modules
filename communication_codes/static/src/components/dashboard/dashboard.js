/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Layout } from "@web/search/layout";
import { useService } from "@web/core/utils/hooks";
import { Component, onWillStart, onMounted, useRef, useState } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";


const STATUS_KEYS = ['in_stock', 'delivered', 'suspended', 'cancelled'];
const SYSTEM_KEYS = ['prepaid', 'monthly_invoice', 'other'];


export class CommunicationCodesDashboard extends Component {
    static template = "communication_codes.Dashboard";
    static components = { Layout };

    setup() {
        this.action = useService("action");
        this.orm = useService("orm");

        this.state = useState({
            stats: {},
            loading: true,
            lastUpdate: new Date().toLocaleString('en-US', {
                hour: '2-digit',
                minute: '2-digit',
                hour12: true
            }),
        });

        this.statusChartRef = useRef("statusChart");
        this.systemChartRef = useRef("systemChart");

        this.charts = {
            status: null,
            system: null,
        };

        onWillStart(() => this.loadStats());
        onMounted(() => {
            setTimeout(() => this.initCharts(), 100);
        });
    }

    async loadStats() {
        try {
            const data = await this.orm.call(
                "communication.codes",
                "get_dashboard_stats",
                []
            );
            this.state.stats = data;
            this.state.loading = false;
            this.state.lastUpdate = new Date().toLocaleString('en-US', {
                hour: '2-digit',
                minute: '2-digit',
                hour12: true
            });
        } catch (error) {
            console.error("Failed to load dashboard stats:", error);
            this.state.loading = false;
        }
    }

    initCharts() {
        if (this.state.loading) return;
        if (!this.state.stats.total_count) return;

        if (window.Chart && this.statusChartRef.el && this.systemChartRef.el) {
            this.renderStatusChart();
            this.renderSystemChart();
        }
    }

    renderStatusChart() {
        if (this.charts.status) {
            this.charts.status.destroy();
        }

        const ctx = this.statusChartRef.el.getContext('2d');
        this.charts.status = new window.Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['In Stock', 'Delivered', 'Suspended', 'Cancelled'],
                datasets: [{
                    data: STATUS_KEYS.map(
                        key => this.state.stats.status_counts?.[key] || 0
                    ),
                    backgroundColor: [
                        '#10b981',
                        '#3b82f6',
                        '#f59e0b',
                        '#ef4444'
                    ],
                    borderWidth: 0,
                    hoverOffset: 4,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '65%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true,
                            pointStyle: 'circle',
                            font: {
                                family: "'Inter', sans-serif",
                                size: 12
                            }
                        }
                    }
                },
                onClick: (evt, activeElements) => {
                    if (activeElements.length > 0) {
                        const status = STATUS_KEYS[activeElements[0].index];
                        this.openView(status);
                    }
                }
            }
        });
    }

    renderSystemChart() {
        if (this.charts.system) {
            this.charts.system.destroy();
        }

        const ctx = this.systemChartRef.el.getContext('2d');
        this.charts.system = new window.Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Prepaid', 'Monthly Invoice', 'Other'],
                datasets: [{
                    data: SYSTEM_KEYS.map(
                        key => this.state.stats.system_counts?.[key] || 0
                    ),
                    backgroundColor: [
                        '#6366f1',
                        '#8b5cf6',
                        '#a855f7'
                    ],
                    borderWidth: 0,
                    hoverOffset: 4,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '60%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 15,
                            usePointStyle: true,
                            pointStyle: 'circle',
                            font: {
                                family: "'Inter', sans-serif",
                                size: 11
                            }
                        }
                    }
                },
                onClick: (evt, activeElements) => {
                    if (activeElements.length > 0) {
                        const system = SYSTEM_KEYS[activeElements[0].index];
                        this.openSystemView(system);
                    }
                }
            }
        });
    }

    async openView(status = null) {
        const domain = status ? [['code_status', '=', status]] : [];
        await this.action.doAction({
            type: 'ir.actions.act_window',
            name: _t('Communication Codes'),
            res_model: 'communication.codes',
            view_mode: 'list,form',
            views: [[false, 'list'], [false, 'form']],
            domain: domain,
            target: 'current',
        });
    }

    async openSystemView(system) {
        await this.action.doAction({
            type: 'ir.actions.act_window',
            name: _t('Communication Codes'),
            res_model: 'communication.codes',
            view_mode: 'list,form',
            views: [[false, 'list'], [false, 'form']],
            domain: [['code_system', '=', system]],
            target: 'current',
        });
    }
}


registry.category("actions").add("communication_codes_dashboard", CommunicationCodesDashboard);
