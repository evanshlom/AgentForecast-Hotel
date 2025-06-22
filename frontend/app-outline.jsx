// ========== REACT HOOKS IMPORT ==========
// Destructuring the hooks we need from React (already loaded in HTML)
const { useState, useEffect, useRef } = React;

// ========== MAIN APP COMPONENT ==========
function App() {
    // ========== STATE MANAGEMENT ==========
    
    // Messages array - stores all chat messages
    // Initialize with welcome message
    const [messages, setMessages] = useState([
        {
            type: 'ai',
            text: 'Welcome to Wynn Resort Forecast AI! (Not connected - skeleton only)'
        }
    ]);
    
    // Input field value - controlled component pattern
    const [inputValue, setInputValue] = useState('');
    
    // ========== REFS FOR DOM ACCESS ==========
    
    // Reference to canvas element for Chart.js
    const chartRef = useRef(null);
    
    // Reference to invisible div at end of messages for auto-scrolling
    const messagesEndRef = useRef(null);

    // ========== SIDE EFFECTS ==========
    
    // Auto-scroll to bottom when new messages arrive
    useEffect(() => {
        // Scroll to bottom when messages change
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);  // Dependency array - runs when messages change

    // Initialize Chart.js on component mount
    useEffect(() => {
        // Create empty chart
        if (chartRef.current) {
            const ctx = chartRef.current.getContext('2d');
            
            // Chart.js configuration
            new Chart(ctx, {
                type: 'line',  // Line chart for time series data
                
                // ===== CHART DATA STRUCTURE =====
                data: {
                    // X-axis labels (168 hours = 7 days)
                    labels: ['Hour 1', 'Hour 2', 'Hour 3', '...', 'Hour 168'],
                    
                    // Multiple datasets for different metrics
                    datasets: [
                        {
                            label: 'Room Occupancy (%)',
                            data: [],  // Empty for skeleton
                            borderColor: '#DAA520',  // Goldenrod
                            backgroundColor: 'rgba(218, 165, 32, 0.1)'  // Transparent fill
                        },
                        {
                            label: 'Cleaning Staff Needed',
                            data: [],  // Empty for skeleton
                            borderColor: '#4169E1',  // Royal Blue
                            backgroundColor: 'rgba(65, 105, 225, 0.1)'
                        },
                        {
                            label: 'Security Staff Needed',
                            data: [],  // Empty for skeleton
                            borderColor: '#DC143C',  // Crimson
                            backgroundColor: 'rgba(220, 20, 60, 0.1)'
                        }
                    ]
                },
                
                // ===== CHART OPTIONS =====
                options: {
                    responsive: true,  // Resizes with container
                    maintainAspectRatio: false,  // Allows height control
                    
                    plugins: {
                        title: {
                            display: true,
                            text: 'Wynn Resort 7-Day Hourly Forecast (No Data Yet)'
                        }
                    },
                    
                    scales: {
                        y: {
                            title: {
                                display: true,
                                text: 'Units / Percentage'
                            }
                        }
                    }
                }
            });
        }
    }, []);  // Empty dependency array - runs once on mount

    // ========== EVENT HANDLERS ==========
    
    // Handle message sending
    const sendMessage = () => {
        // Ignore empty messages
        if (!inputValue.trim()) return;

        // Add user message to chat
        setMessages(prev => [...prev, {
            type: 'user',
            text: inputValue
        }]);

        // Simulate AI response after 500ms delay
        // (In production, this would be an API call)
        setTimeout(() => {
            setMessages(prev => [...prev, {
                type: 'ai',
                text: 'Backend not connected. This is just the UI skeleton for the tutorial.'
            }]);
        }, 500);

        // Clear input field
        setInputValue('');
    };

    // Handle Enter key press in input field
    const handleKeyPress = (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    };

    // ========== COMPONENT RENDER ==========
    return (
        <div className="container">
            {/* ===== LEFT SIDE: CHAT INTERFACE ===== */}
            <div className="chat-panel">
                {/* Chat Header */}
                <div className="chat-header">
                    Wynn Resort Forecast AI 🎰
                </div>
                
                {/* Messages Area */}
                <div className="chat-messages">
                    {/* Map over messages array to render each message */}
                    {messages.map((msg, idx) => (
                        <div key={idx} className={`message ${msg.type}-message`}>
                            {msg.text}
                        </div>
                    ))}
                    {/* Invisible div for auto-scroll target */}
                    <div ref={messagesEndRef} />
                </div>
                
                {/* Input Area */}
                <div className="chat-input">
                    <input
                        type="text"
                        value={inputValue}  // Controlled component
                        onChange={(e) => setInputValue(e.target.value)}
                        onKeyPress={handleKeyPress}
                        placeholder="Type a message..."
                    />
                    <button onClick={sendMessage}>
                        Send
                    </button>
                </div>
            </div>
            
            {/* ===== RIGHT SIDE: CHART DISPLAY ===== */}
            <div className="chart-panel">
                <div className="chart-container">
                    <h2>Resort Operations Forecast</h2>
                    
                    {/* Chart Canvas Container */}
                    <div style={{ height: '400px', position: 'relative' }}>
                        <canvas ref={chartRef}></canvas>
                    </div>
                    
                    {/* Placeholder text while no data */}
                    <div className="placeholder">
                        <p>Chart will display 168-hour forecast once backend is connected</p>
                    </div>
                </div>
            </div>
        </div>
    );
}

// ========== RENDER APP TO DOM ==========
// Mount the React app to the 'root' div in index.html
ReactDOM.render(<App />, document.getElementById('root'));