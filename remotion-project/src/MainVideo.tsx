import React from "react";
import {
  AbsoluteFill,
  Audio,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import manifest from "../public/audio/manifest.json";

export const MainVideo: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const hookOpacity = interpolate(frame, [0, 15], [0, 1], { extrapolateRight: "clamp" });
  const keywordScale = spring({ frame: frame - 20, fps, config: { damping: 12 } });
  const scriptOpacity = interpolate(frame, [45, 65], [0, 1], { extrapolateRight: "clamp" });

  return (
    <AbsoluteFill
      style={{
        background: "linear-gradient(180deg, #1A2980 0%, #26D0CE 100%)",
        fontFamily: "Arial, sans-serif",
        color: "white",
        padding: 80,
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      <div style={{ opacity: hookOpacity, fontSize: 48, fontWeight: 700, textAlign: "center", marginBottom: 40 }}>
        {manifest.hook}
      </div>

      <div
        style={{
          transform: `scale(${keywordScale})`,
          fontSize: 64,
          fontWeight: 900,
          textAlign: "center",
          textTransform: "uppercase",
          letterSpacing: 2,
          marginBottom: 60,
          color: "#FFEB3B",
        }}
      >
        {manifest.keyword}
      </div>

      <div
        style={{
          opacity: scriptOpacity,
          fontSize: 36,
          lineHeight: 1.5,
          textAlign: "center",
          maxWidth: 900,
        }}
      >
        {manifest.script}
      </div>

      <div
        style={{
          position: "absolute",
          bottom: 60,
          fontSize: 22,
          opacity: 0.8,
          textAlign: "center",
        }}
      >
        Educational content only — not investment advice. #SmartInvestingIndia
      </div>

      {manifest.audioFile && <Audio src={staticFile(`audio/${manifest.audioFile}`)} />}
    </AbsoluteFill>
  );
};
