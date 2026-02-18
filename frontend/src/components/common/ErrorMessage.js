import React from 'react';

const ErrorMessage = ({ title = 'Error', message, onRetry }) => {
    return (
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 my-4">
            <div className="flex items-start">
                <div className="flex-shrink-0">
                    <svg className="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                </div>
                <div className="ml-3 flex-1">
                    <h3 className="text-sm font-medium text-red-800">{title}</h3>
                    <p className="mt-2 text-sm text-red-700">{message}</p>
                    {onRetry && (
                        <button
                            onClick={onRetry}
                            className="mt-3 text-sm font-medium text-red-600 hover:text-red-500"
                        >
                            Try again →
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
};

export default ErrorMessage;
