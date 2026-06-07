import { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [videoUrl, setVideoUrl] = useState("");
  const [captions, setCaptions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);

  // Active Main Right Sidebar Tab State
  const [activeTab, setActiveTab] = useState("Templates"); 
  
  // Left Menu State Tracker
  const [leftMenu, setLeftMenu] = useState("Captions");

  // Accordion Sections Open/Close States (Right Sidebar)
  const [sections, setSections] = useState({
    fonts: true,
    format: true,
    position: true,
    color: false,
    emphasis: false,
    spacing: false,
    effects: false
  });

  // Dynamic Stylings Properties state connected directly to preview overlay
  const [fontFamily, setFontFamily] = useState("Inter"); 
  const [fontFace, setFontFace] = useState("Extra Bold");
  const [fontSize, setFontSize] = useState(27); 
  const [textAlign, setTextAlign] = useState("center");
  const [positionX, setPositionX] = useState(50.0);
  const [positionY, setPositionY] = useState(70.0); 
  const [fontColor, setFontColor] = useState("#ffffff");
  const [glowColor, setGlowColor] = useState("#4ade80"); 
  const [textTransform, setTextTransform] = useState("lowercase"); 
  const [activeTemplate, setActiveTemplate] = useState("premium");

  const toggleSection = (sec) => {
    setSections(prev => ({ ...prev, [sec]: !prev[sec] }));
  };

  const templates = [
    { name: "premium", color: "#ffffff", shadow: "0 0 25px rgba(74, 222, 128, 0.8)", activeColor: "#4ade80" },
    { name: "Kalakar Glow", color: "#ffffff", shadow: "0 0 16px #7CFF00", activeColor: "#7CFF00" },
    { name: "Ali Abdaal", color: "#ffffff", shadow: "none", bg: "#111111", activeColor: "#ffffff" }
  ];

  // 1. DYNAMIC EDIT WORD FUNCTION
  const handleEditWord = (captionIndex, wordIndex) => {
    const currentWord = captions[captionIndex].words[wordIndex].word;
    const newWordText = prompt("✏️ Edit word text:", currentWord);
    
    if (newWordText !== null && newWordText.trim() !== "") {
      setCaptions(prevCaptions => 
        prevCaptions.map((caption, idx) => {
          if (idx === captionIndex) {
            const updatedWords = [...caption.words];
            updatedWords[wordIndex] = { ...updatedWords[wordIndex], word: newWordText.trim() };
            return { ...caption, words: updatedWords };
          }
          return caption;
        })
      );
    }
  };

  // 2. DYNAMIC ADD WORD FUNCTION (INSERTED NEXT TO THE HOVERED WORD)
  const handleAddWordAfter = (captionIndex, wordIndex) => {
    const newWordText = prompt("➕ Enter new word to add after this word:");
    if (newWordText !== null && newWordText.trim() !== "") {
      setCaptions(prevCaptions => 
        prevCaptions.map((caption, idx) => {
          if (idx === captionIndex) {
            const updatedWords = [...caption.words];
            const targetWord = updatedWords[wordIndex];
            
            const startTime = targetWord ? targetWord.end : caption.start;
            const endTime = startTime + 0.6;

            const newWordObj = {
              word: newWordText.trim(),
              start: startTime,
              end: endTime,
              highlight: false
            };

            // Insert directly inside array after the active index
            updatedWords.splice(wordIndex + 1, 0, newWordObj);
            return { ...caption, words: updatedWords };
          }
          return caption;
        })
      );
    }
  };

  // 3. DYNAMIC DELETE WORD FUNCTION
  const handleDeleteWord = (captionIndex, wordIndex) => {
    if (window.confirm("❌ Are you sure you want to delete this word?")) {
      setCaptions(prevCaptions => 
        prevCaptions.map((caption, idx) => {
          if (idx === captionIndex) {
            const updatedWords = caption.words.filter((_, wIdx) => wIdx !== wordIndex);
            return { ...caption, words: updatedWords };
          }
          return caption;
        }).filter(caption => caption.words.length > 0) // Remove whole line if empty
      );
    }
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (!selectedFile) return;
    setFile(selectedFile);
    setVideoUrl(URL.createObjectURL(selectedFile));
  };

const handleGenerate = async () => {
  if (!file) return alert("Select a video!");
  setLoading(true);

  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await fetch("https://caption-production.up.railway.app/", {
      method: "POST", // Yahan hum 'fetch' use kar rahe hain taaki axios ka conflict khatam ho
      body: formData,
    });

    const result = await response.json();
    if (response.ok) {
      setCaptions(result.captions || []);
    } else {
      console.error("Server Error:", result);
      alert("Error: " + JSON.stringify(result));
    }
  } catch (error) {
    console.error("Network Error:", error);
  }
  setLoading(false);
};

  // FINDING THE DYNAMIC ACTIVE WORD TO RENDER PREMIUM ANIMATION
  let currentActiveWordObj = null;
  captions.forEach(caption => {
    caption.words?.forEach(w => {
      if (currentTime >= w.start && currentTime <= w.end) {
        currentActiveWordObj = w;
      }
    });
  });

  const isPremiumHighlight = activeTemplate === "premium" && (currentActiveWordObj?.highlight || (currentActiveWordObj && currentActiveWordObj.word.length > 4));

  return (
    <div className="app">
      {/* 1. TOP HEADER BRANDING BAR */}
   <div className="topbar">
  <div className="topbar-left">
    <div className="home-icon">🏠</div>
    <span className="project-title">0601</span>
  </div>
  <div className="topbar-center">
    <label className="action-btn file-label">
      Choose Video
      <input type="file" accept="video/*" onChange={handleFileChange} style={{display: "none"}} />
    </label>
    <button onClick={handleGenerate} className="action-btn generate-btn">
      {loading ? "⚡ Generating..." : "✨ Generate Captions"}
    </button>
  </div>
  {/* Upgrade button aur Profile avatar yahan se hata diye gaye hain */}
  <div className="topbar-right"></div>
</div>

      {/* 2. MAIN APPLICATION WORKSPACE HUB */}
      <div className="main-layout">
        
        {/* LEFT VERTICAL NAVBAR */}
        <div className="left-sidebar-menu">
          <div className={`menu-item ${leftMenu === "Captions" ? "active" : ""}`} onClick={() => setLeftMenu("Captions")}>
            <div className="icon">📝</div>
            <span>Captions</span>
          </div>
          <div className={`menu-item ${leftMenu === "Fonts" ? "active" : ""}`} onClick={() => setLeftMenu("Fonts")}>
            <div className="icon">🔤</div>
            <span>Custom Fonts</span>
          </div>
          <div className={`menu-item ${leftMenu === "Audio" ? "active" : ""}`} onClick={() => setLeftMenu("Audio")}>
            <div className="icon">🎵</div>
            <span>Audio</span>
          </div>
        </div>

        {/* EDITOR WORKSPACE CONSOLE */}
        <div className="editor-workspace">
          
          <div className="upper-workspace-region">
            
            {/* LEFT: CAPTIONS SCROLLER FEED */}
            <div className="captions-manager-panel">
              <div className="panel-header-row">
                <h3>Captions</h3>
                <div className="search-tool-trigger">🔍</div>
                <button className="caption-tools-btn">⚙ Tools ▾</button>
              </div>
              <p style={{ fontSize: "10px", color: "#8e8e93", padding: "0 12px 10px" }}>
                *Hover over any word to Add, Edit, or Delete
              </p>

              <div className="captions-feed-scroller">
                {captions.map((caption, index) => (
                  <div key={index} className="caption-card-node" style={{ display: "flex", flexDirection: "column", padding: "12px", borderBottom: "1px solid #222" }}>
                    <span className="node-index" style={{ color: "#4ade80", fontSize: "11px", fontWeight: "bold", marginBottom: "6px" }}>
                      Line {index + 1}
                    </span>
                    
                    <div className="node-content-block">
                      <div className="word-pills-row" style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
                        {caption.words?.map((w, wi) => (
                          <div 
                            key={wi} 
                            className="word-pill-hover-container"
                            style={{ position: "relative", display: "inline-block" }}
                          >
                            {/* main pill shape */}
                            <span 
                              className={`word-pill ${currentTime >= w.start && currentTime <= w.end ? "playing" : ""} ${w.highlight ? "premium-target" : ""}`}
                              onClick={() => {
                                w.highlight = !w.highlight;
                                setCaptions([...captions]);
                              }}
                              style={{ cursor: "pointer", display: "inline-block" }}
                            >
                              {w.word}
                            </span>

                            {/* HOVER ACTION FLOATING TOOLBAR */}
                            <div className="word-hover-actions">
                              <button onClick={(e) => { e.stopPropagation(); handleEditWord(index, wi); }} title="Edit Word">✏️</button>
                              <button onClick={(e) => { e.stopPropagation(); handleAddWordAfter(index, wi); }} title="Add Word After">➕</button>
                              <button onClick={(e) => { e.stopPropagation(); handleDeleteWord(index, wi); }} title="Delete Word" style={{ color: "#ef4444" }}>❌</button>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                ))}
                {captions.length === 0 && <p className="empty-notice">Click 'Generate Captions' to start.</p>}
              </div>
            </div>

            {/* CENTER: VIDEO PREVIEW DISPLAY FRAME */}
            <div className="live-preview-panel">
              <div className="media-screen-wrapper">
                {videoUrl ? (
                  <video src={videoUrl} className="video-viewport" onTimeUpdate={(e) => setCurrentTime(e.target.currentTime)} controls />
                ) : (
                  <div className="empty-media-placeholder">
                    <p>No Active Video Frame Loaded</p>
                  </div>
                )}

                {/* OVERLAY LAYER */}
                {currentActiveWordObj && (
                  <div 
                    key={currentActiveWordObj.word} 
                    className={`live-caption-overlay premium-word-animation ${isPremiumHighlight ? "premium-highlight-punch" : "premium-normal-punch"}`}
                    style={{
                      left: `${positionX}%`,
                      top: `${positionY}%`,
                      transform: "translate(-50%, -50%)",
                      textAlign: textAlign,
                      fontFamily: fontFamily,
                      fontSize: isPremiumHighlight ? `${fontSize * 1.5}px` : `${fontSize}px`,
                      fontWeight: fontFace === "Extra Bold" ? "900" : "700",
                      color: isPremiumHighlight ? glowColor : fontColor,
                      textTransform: isPremiumHighlight ? "uppercase" : textTransform,
                      textShadow: isPremiumHighlight 
                        ? `0 0 20px ${glowColor}, 2px 2px 4px rgba(0,0,0,0.9)`
                        : `1px 1px 3px rgba(0,0,0,0.8)`
                    }}
                  >
                    {currentActiveWordObj.word}
                  </div>
                )}
              </div>
            </div>

          </div>

          {/* BOTTOM TIMELINE CONTROLS */}
          <div className="timeline-dashboard-container">
            <div className="timeline-toolbar">
              <div className="left-tools">
                <button className="tool-btn">T</button>
                <button className="tool-btn">✂</button>
              </div>
              <div className="right-tools">
                <input type="range" className="zoom-slider" />
              </div>
            </div>

            <div className="timeline-scroll-track">
              <div className="audio-wave-vector-bg">
                {captions.map((caption, index) => (
                  <div key={index} className="timeline-track-segment" style={{minWidth: "140px"}}>
                    <div className="segment-label">{caption.text}</div>
                    <div className="word-sub-blocks-strip">
                      {caption.words?.map((w, wi) => (
                        <div key={wi} className={`mini-word-block ${currentTime >= w.start && currentTime <= w.end ? "active" : ""}`}>
                          {w.word}
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

        </div>

        {/* RIGHT CONTROL SIDEBAR */}
       <div className="right-inspector-panel">
  <div className="inspector-tabs-nav">
    {/* Sirf Text aur Templates rakha hai */}
    {["Text", "Templates", "Transitions"].map((tab) => (
      <button 
        key={tab} 
        className={`tab-nav-btn ${activeTab === tab ? "active" : ""}`} 
        onClick={() => setActiveTab(tab)}
      >
        {tab}
      </button>
    ))}
  </div>

          <div className="inspector-panel-scroller">
           {activeTab === "Text" && (
  <div className="inspector-panel-scroller">
    {/* 1. FONTS Section */}
 <div className="accordion-section">
  <div className="accordion-header" onClick={() => toggleSection("fonts")}>
    <span>{sections.fonts ? "▼" : "▶"} FONTS</span>
  </div>
  {sections.fonts && (
    <div className="accordion-body-content">
      <label className="inspector-label">Font Family</label>
      <select value={fontFamily} onChange={(e) => setFontFamily(e.target.value)}>
        <option value="Inter">Inter</option>
        <option value="Impact">Impact</option>
        <option value="Arial">Arial</option>
        <option value="Roboto">Roboto</option>
        <option value="Montserrat">Montserrat</option>
        <option value="Poppins">Poppins</option>
        <option value="Oswald">Oswald</option>
        <option value="Bebas Neue">Bebas Neue</option>
        <option value="Dancing Script">Dancing Script</option>
      </select>
    </div>
  )}
</div>

    {/* 2. FORMAT Section */}
    <div className="accordion-section">
  <div className="accordion-header" onClick={() => toggleSection("format")}>
    <span>{sections.format ? "▼" : "▶"} FORMAT</span>
  </div>
  {sections.format && (
    <div className="accordion-body-content">
      
      {/* --- YAHAN TEXT SIZE SLIDER ADD KIYA HAI --- */}
      <label className="inspector-label">Text Size</label>
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '15px' }}>
        <input 
          type="range" 
          min="10" 
          max="100" 
          value={fontSize} 
          onChange={(e) => setFontSize(Number(e.target.value))}
          style={{ flex: 1, cursor: 'pointer' }}
        />
        <span style={{ fontSize: '12px', color: '#4ade80', fontWeight: 'bold', background: '#18181b', padding: '2px 6px', borderRadius: '4px' }}>
          {fontSize}px
        </span>
      </div>

      {/* Tumhara purana Styles code safe hai */}
      <label className="inspector-label">Styles</label>
      <div className="segmented-control">
        <button className={textTransform === "uppercase" ? "active" : ""} onClick={() => setTextTransform("uppercase")}>Tt</button>
        <button>T</button>
        <button className={textTransform === "lowercase" ? "active" : ""} onClick={() => setTextTransform("lowercase")}>t</button>
        <button>U</button>
      </div>

      {/* Tumhara purana Text Alignment code safe hai */}
      <label className="inspector-label">Text Alignment</label>
      <div className="segmented-control">
        <button className={textAlign === "left" ? "active" : ""} onClick={() => setTextAlign("left")}>≡</button>
        <button className={textAlign === "center" ? "active" : ""} onClick={() => setTextAlign("center")}>≡</button>
        <button className={textAlign === "right" ? "active" : ""} onClick={() => setTextAlign("right")}>≡</button>
      </div>

    </div>
  )}
</div>

    {/* 3. POSITION Section */}
    <div className="accordion-section">
      <div className="accordion-header" onClick={() => toggleSection("position")}><span>{sections.position ? "▼" : "▶"} POSITION</span></div>
      {sections.position && (
        <div className="accordion-body-content">
          <div className="coordinate-inputs-pair">
            <div className="coord-field"><label>X (%)</label><input type="number" value={positionX} onChange={(e) => setPositionX(Number(e.target.value))} /></div>
            <div className="coord-field"><label>Y (%)</label><input type="number" value={positionY} onChange={(e) => setPositionY(Number(e.target.value))} /></div>
          </div>
        </div>
      )}
    </div>

    {/* 4. COLOR Section (NEW) */}
    <div className="accordion-section">
      <div className="accordion-header" onClick={() => toggleSection("color")}><span>{sections.color ? "▼" : "▶"} COLOR</span></div>
      {sections.color && (
        <div className="accordion-body-content">
          <div className="color-mode-toggle"><button className="active">Solid</button><button>Gradient</button></div>
          <div style={{display: 'flex', alignItems: 'center', gap: '10px'}}>
             <input type="color" value={fontColor} onChange={(e) => setFontColor(e.target.value)} />
             <input type="text" value={fontColor} readOnly style={{background: '#18181b', border: 'none', color: '#fff', padding: '5px', borderRadius: '4px', width: '100%'}} />
          </div>
        </div>
      )}
    </div>

    {/* 5. SPACING Section (NEW) */}
    <div className="accordion-section">
      <div className="accordion-header" onClick={() => toggleSection("spacing")}><span>{sections.spacing ? "▼" : "▶"} SPACING</span></div>
      {sections.spacing && (
        <div className="accordion-body-content">
          <label className="inspector-label">Letter Spacing</label>
          <div className="slider-row"><input type="range" min="0" max="10" /><span className="value-badge">0</span></div>
          <label className="inspector-label" style={{marginTop: '10px'}}>Line Spacing</label>
          <div className="slider-row"><input type="range" min="0" max="2" step="0.1" /><span className="value-badge">0.9</span></div>
        </div>
      )}
    </div>

    {/* 6. EFFECTS Section (NEW) */}
    <div className="accordion-section">
      <div className="accordion-header" onClick={() => toggleSection("effects")}><span>{sections.effects ? "▼" : "▶"} EFFECTS</span></div>
      {sections.effects && (
        <div className="accordion-body-content">
          <p style={{fontSize: '11px', color: '#71717a'}}>No effects applied</p>
        </div>
      )}
    </div>
  </div>
)}

            {activeTab === "Templates" && (
              <div className="templates-tab-view">
                <div className="presets-filter-toggle">
                  <button className="filter-pill active">Built-in Templates</button>
                  <button className="filter-pill">My Presets</button>
                </div>
                <input type="text" className="search-template-input" placeholder="Find a template..." />

                <div className="templates-grid-feed">
                  {templates.map((t) => (
                    <div 
                      key={t.name} 
                      className={`template-card-item ${activeTemplate === t.name ? "selected-premium-border" : ""}`} 
                      onClick={() => {
                        setActiveTemplate(t.name);
                        setGlowColor(t.activeColor);
                      }}
                    >
                      <div className="template-title-flex">
                        <h4>{t.name}</h4>
                        {t.name === "premium" && <span className="premium-badge">NEW</span>}
                      </div>
                      <div className="template-preview-box" style={{backgroundColor: t.bg || "#18181b"}}>
                        <div className="premium-preview-stack">
                          <span style={{color: t.color, fontSize: '11px'}}>Normal</span>
                          <span style={{color: t.activeColor, fontWeight: '900', textShadow: t.shadow, fontSize: '13px'}}>PREMIUM</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          <div className="inspector-footer-action">
            <button className="export-system-btn">Export</button>
          </div>
        </div>

      </div>
    </div>
  );
}

export default App;
