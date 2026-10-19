import React from "react";
import { Composition } from "remotion";
import { MainVideo } from "./MainVideo";
import manifest from "../public/audio/manifest.json";

const FPS = 30;
// A little padding beyond the spoken audio so the final frame doesn't cut off abruptly.
const DURATION_IN_FRAMES = Math.max(60, Math.ceil((manifest.durationSeconds + 1.5) * FPS));

export const Root: React.FC = () => {
  return (
    <Composition
      id="MainVideo"
      component={MainVideo}
      durationInFrames={DURATION_IN_FRAMES}
      fps={FPS}
      width={1080}
      height={1920}
    />
  );
};
