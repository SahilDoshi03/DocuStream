'use client';

import React, { useState } from 'react';
import Nango from '@nangohq/frontend';

// We assume we are using the 'google-drive' integration
const INTEGRATION_ID = 'google-drive';

export function GoogleDriveConnect() {
    const [loading, setLoading] = useState(false);
    const [connected, setConnected] = useState(false);

    const handleConnect = async () => {
        setLoading(true);
        try {
            // 1. Fetch Connect Session Token from Backend
            const response = await fetch('http://localhost:8000/api/nango/connect-token'); // Adjust URL for env
            if (!response.ok) {
                throw new Error('Failed to fetch session token');
            }
            const { token } = await response.json();

            console.log('DEBUG: Received token:', token);

            // 2. Initialize Nango with the session token
            // Passing connectSessionToken during initialization
            const nango = new Nango({
                host: 'https://api.nango.dev',
                connectSessionToken: token
            } as any);

            // 3. Trigger the Auth Flow
            // Now we just call auth. ID is mapped via session.
            const result = await nango.auth(INTEGRATION_ID);
            console.log("DEBUG: Auth Result:", result);

            setConnected(true);
            alert('Google Drive Connected Successfully!');

        } catch (error) {
            console.error('Connection failed:', error);
            alert('Failed to connect Google Drive.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="p-4 border rounded shadow-sm bg-white">
            <h3 className="text-lg font-medium mb-2">Google Drive Integration</h3>
            <p className="text-sm text-gray-500 mb-4">
                Connect your Google Drive to export extracted data directly.
            </p>

            {connected ? (
                <div className="text-green-600 font-semibold">
                    ✓ Connected
                </div>
            ) : (
                <button
                    onClick={handleConnect}
                    disabled={loading}
                    className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 transition-colors"
                >
                    {loading ? 'Connecting...' : 'Connect Google Drive'}
                </button>
            )}
        </div>
    );
}
