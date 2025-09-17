import React, { useState, useEffect } from 'react';
import api from '../../services/api';

interface ServiceHealth {
    status: string;
    response_time?: number;
    error?: string;
    timestamp: string;
}

interface SystemHealth {
    overall_status: string;
    timestamp: string;
    components: {
        database: ServiceHealth;
        redis: ServiceHealth;
        ai_service: ServiceHealth;
    };
}

interface Alert {
    alert_id: string;
    level: string;
    title: string;
    description: string;
    timestamp: string;
    acknowledged: boolean;
    resolved: boolean;
}

const ServiceStatusDashboard: React.FC = () => {
    const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null);
    const [alerts, setAlerts] = useState<Alert[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchSystemHealth = async () => {
        try {
            const response = await api.get('/monitoring/health');
            setSystemHealth(response.data);
            setError(null);
        } catch (err: any) {
            setError(err.message || 'Failed to fetch system health');
        }
    };

    const fetchAlerts = async () => {
        try {
            const response = await api.get('/monitoring/alerts');
            setAlerts(response.data.alerts);
        } catch (err: any) {
            console.error('Failed to fetch alerts:', err);
        }
    };

    const acknowledgeAlert = async (alertId: string) => {
        try {
            await api.post(`/monitoring/alerts/${alertId}/acknowledge`);
            await fetchAlerts(); // Refresh alerts
        } catch (err: any) {
            console.error('Failed to acknowledge alert:', err);
        }
    };

    const resolveAlert = async (alertId: string) => {
        try {
            await api.post(`/monitoring/alerts/${alertId}/resolve`);
            await fetchAlerts(); // Refresh alerts
        } catch (err: any) {
            console.error('Failed to resolve alert:', err);
        }
    };

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            await Promise.all([fetchSystemHealth(), fetchAlerts()]);
            setLoading(false);
        };

        fetchData();

        // Set up polling for real-time updates
        const interval = setInterval(() => {
            fetchSystemHealth();
            fetchAlerts();
        }, 30000); // Update every 30 seconds

        return () => clearInterval(interval);
    }, []);

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'healthy': return 'text-green-600 bg-green-100';
            case 'degraded': return 'text-yellow-600 bg-yellow-100';
            case 'unhealthy': return 'text-red-600 bg-red-100';
            default: return 'text-gray-600 bg-gray-100';
        }
    };

    const getStatusIcon = (status: string) => {
        switch (status) {
            case 'healthy': return '✅';
            case 'degraded': return '⚠️';
            case 'unhealthy': return '❌';
            default: return '❓';
        }
    };

    const getAlertLevelColor = (level: string) => {
        switch (level) {
            case 'critical': return 'border-red-500 bg-red-50 text-red-800';
            case 'error': return 'border-red-400 bg-red-50 text-red-700';
            case 'warning': return 'border-yellow-400 bg-yellow-50 text-yellow-700';
            case 'info': return 'border-blue-400 bg-blue-50 text-blue-700';
            default: return 'border-gray-400 bg-gray-50 text-gray-700';
        }
    };

    if (loading) {
        return (
            <div className="p-6">
                <div className="animate-pulse">
                    <div className="h-8 bg-gray-200 rounded mb-4"></div>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                        {[1, 2, 3].map(i => (
                            <div key={i} className="h-32 bg-gray-200 rounded"></div>
                        ))}
                    </div>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="p-6">
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                    <h3 className="text-red-800 font-medium">Error Loading System Status</h3>
                    <p className="text-red-600 text-sm mt-1">{error}</p>
                    <button
                        onClick={() => window.location.reload()}
                        className="mt-3 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
                    >
                        Retry
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="p-6 space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold text-gray-900">System Status</h1>
                <div className="flex items-center space-x-2">
                    <div className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(systemHealth?.overall_status || 'unknown')}`}>
                        {getStatusIcon(systemHealth?.overall_status || 'unknown')} {systemHealth?.overall_status || 'Unknown'}
                    </div>
                    <span className="text-sm text-gray-500">
                        Last updated: {systemHealth?.timestamp ? new Date(systemHealth.timestamp).toLocaleTimeString() : 'Unknown'}
                    </span>
                </div>
            </div>

            {/* Service Components */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {systemHealth?.components && Object.entries(systemHealth.components).map(([name, component]) => (
                    <div key={name} className="bg-white rounded-lg border border-gray-200 p-4">
                        <div className="flex items-center justify-between mb-2">
                            <h3 className="font-medium text-gray-900 capitalize">{name.replace('_', ' ')}</h3>
                            <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(component.status)}`}>
                                {getStatusIcon(component.status)} {component.status}
                            </span>
                        </div>

                        {component.response_time && (
                            <p className="text-sm text-gray-600">
                                Response time: {(component.response_time * 1000).toFixed(0)}ms
                            </p>
                        )}

                        {component.error && (
                            <p className="text-sm text-red-600 mt-1">
                                Error: {component.error}
                            </p>
                        )}

                        <p className="text-xs text-gray-500 mt-2">
                            Checked: {new Date(component.timestamp).toLocaleTimeString()}
                        </p>
                    </div>
                ))}
            </div>

            {/* Active Alerts */}
            {alerts.length > 0 && (
                <div className="bg-white rounded-lg border border-gray-200">
                    <div className="px-4 py-3 border-b border-gray-200">
                        <h2 className="text-lg font-medium text-gray-900">Active Alerts</h2>
                    </div>

                    <div className="divide-y divide-gray-200">
                        {alerts.map((alert) => (
                            <div key={alert.alert_id} className={`p-4 border-l-4 ${getAlertLevelColor(alert.level)}`}>
                                <div className="flex items-start justify-between">
                                    <div className="flex-1">
                                        <div className="flex items-center space-x-2 mb-1">
                                            <h3 className="font-medium">{alert.title}</h3>
                                            <span className={`px-2 py-1 rounded text-xs font-medium uppercase ${getAlertLevelColor(alert.level)}`}>
                                                {alert.level}
                                            </span>
                                        </div>

                                        <p className="text-sm mb-2">{alert.description}</p>

                                        <p className="text-xs opacity-75">
                                            {new Date(alert.timestamp).toLocaleString()}
                                        </p>
                                    </div>

                                    <div className="flex space-x-2 ml-4">
                                        {!alert.acknowledged && (
                                            <button
                                                onClick={() => acknowledgeAlert(alert.alert_id)}
                                                className="px-3 py-1 bg-white border border-gray-300 rounded text-sm hover:bg-gray-50 transition-colors"
                                            >
                                                Acknowledge
                                            </button>
                                        )}

                                        {!alert.resolved && (
                                            <button
                                                onClick={() => resolveAlert(alert.alert_id)}
                                                className="px-3 py-1 bg-green-600 text-white rounded text-sm hover:bg-green-700 transition-colors"
                                            >
                                                Resolve
                                            </button>
                                        )}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* No Alerts Message */}
            {alerts.length === 0 && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-center">
                    <div className="text-green-600 text-4xl mb-2">🎉</div>
                    <h3 className="text-green-800 font-medium">All Systems Operational</h3>
                    <p className="text-green-600 text-sm">No active alerts or issues detected.</p>
                </div>
            )}
        </div>
    );
};

export default ServiceStatusDashboard;