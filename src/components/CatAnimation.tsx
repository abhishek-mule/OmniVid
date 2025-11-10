import React from 'react';
import './CatAnimation.css';

const CatAnimation: React.FC = () => {
  return (
    <div className="cat-animation">
      <div className="all-wrap">  
        <div className="all">
          <div className="yarn"></div>
          <div className="cat-wrap">    
            <div className="cat">
              <div className="cat-upper">
                <div className="cat-leg"></div>
                <div className="cat-leg"></div>
                <div className="cat-head">
                  <div className="cat-ears">
                    <div className="cat-ear"></div>
                    <div className="cat-ear"></div>
                  </div>
                  <div className="cat-face">
                    <div className="cat-eyes"></div>
                    <div className="cat-mouth"></div>
                    <div className="cat-whiskers"></div>
                  </div>
                </div>
              </div>
              <div className="cat-lower-wrap">
                <div className="cat-lower">
                  {[1, 2].map((_, i) => (
                    <div key={i} className="cat-leg">
                      {[...Array(15)].map((_, i) => (
                        <div key={i} className="cat-leg">
                          {i === 14 && <div className="cat-paw"></div>}
                        </div>
                      ))}
                    </div>
                  ))}
                  <div className="cat-tail">
                    {[...Array(15)].map((_, i) => (
                      <div key={i} className={`cat-tail${i === 14 ? ' -end' : ''}`}></div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CatAnimation;
