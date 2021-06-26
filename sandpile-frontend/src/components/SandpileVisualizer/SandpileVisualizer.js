import React from "react";
import useSandpileVisualizer from "./SandpileVisualizer.hooks";

const SandpileVisualizer = () => {
  //const { image } = useSandpileVisualizer();
  return (
    <div>
      <img
        src="http://localhost:5000/plots"
        alt="No image found"
        width={640}
        height={480}
      />
    </div>
  );
};

export default SandpileVisualizer;
