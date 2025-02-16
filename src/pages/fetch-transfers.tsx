import React, { useState } from 'react';

export default function FetchTransfersPage() {
  const [transfersData, setTransfersData] = useState<any>(null);
  const [transfersLoading, setTransfersLoading] = useState<boolean>(false);
  const [transfersError, setTransfersError] = useState<string>('');

  const fetchTransfers = async () => {
    setTransfersLoading(true);
    setTransfersError('');
    try {
      const response = await fetch('http://127.0.0.1:5000/fetchTransfer');
      const data = await response.json();
      setTransfersData(data);
    } catch (error: any) {
      setTransfersError(error.message);
    }
    setTransfersLoading(false);
  };

  return (
    <div className="min-h-screen bg-yellow-100 flex justify-center items-center p-6">
      <div className="bg-white rounded-lg shadow-lg p-6 max-w-4xl w-full h-[600px]">
        <h1 className="text-2xl font-bold mb-4 pixel-font">Fetch Transfers</h1>
        <button
          onClick={fetchTransfers}
          className="bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600 pixel-font"
          disabled={transfersLoading}
        >
          {transfersLoading ? "Loading..." : "Fetch Transfers"}
        </button>
        {transfersError && (
          <p className="mt-4 text-red-500 pixel-font">Error: {transfersError}</p>
        )}
        {transfersData && (
          <pre className="mt-4 bg-gray-100 p-4 rounded text-xs pixel-font overflow-auto whitespace-pre-wrap break-words h-[400px]">
            {JSON.stringify(transfersData, null, 2)}
          </pre>
        )}
      </div>
    </div>
  );
}