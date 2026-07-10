import React, { useState } from 'react';
import StructuredForm from './StructuredForm';
import ChatInterface from './ChatInterface';
import InteractionList from './InteractionList';

const TABS = [
  { key: 'form', label: 'Structured Form' },
  { key: 'chat', label: 'Chat Interface' },
  { key: 'list', label: 'All Interactions' },
];

export default function LogInteractionScreen() {
  const [activeTab, setActiveTab] = useState('form');

  return (
    <div className="log-interaction-screen">
      <h1 className="screen-title">Log Interaction</h1>

      <div className="tab-bar">
        {TABS.map((tab) => (
          <button
            key={tab.key}
            className={`tab-btn ${activeTab === tab.key ? 'tab-btn--active' : ''}`}
            onClick={() => setActiveTab(tab.key)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <div className="panels">
        {activeTab === 'list' ? (
          <div className="panel panel--full">
            <InteractionList />
          </div>
        ) : (
          <>
            <div className="panel panel--form">
              {activeTab === 'form' ? (
                <StructuredForm />
              ) : (
                <div className="panel-placeholder">
                  <StructuredForm />
                </div>
              )}
            </div>
            <div className="panel panel--chat">
              {activeTab === 'chat' ? (
                <ChatInterface />
              ) : (
                <div className="panel-placeholder">
                  <ChatInterface />
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
