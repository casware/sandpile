import React, { useState } from "react";

const useSandPileOptions = () => {
  // Handle the UI data for the Sandpile options form
  const [iterations, setIterations] = useState(100);
  const [grainsPerIteration, setGrainsPerIteration] = useState(1);
  const [loading, setLoading] = useState(false);
  const [grid, setGrid] = useState([]);

  const isPositiveInteger = numericValue => {
    return (
      !Number.isNaN(numericValue) &&
      numericValue > 0 &&
      Number.isInteger(numericValue)
    );
  };

  const setPositiveInteger = ({ value, setterFunction }) => {
    // Generic function for
    console.log(value)
    // const testValidValue = isPositiveInteger(value);
    // console.log(testValidValue);
    // if (!testValidValue) {
    //   // Make sure only positive, integer values are entered
    //   return;
    // }

    console.log("Setting value");
    setterFunction(value);
    return value;
  };

  const handleIterationsChange = numericValue =>
    setPositiveInteger({ value: numericValue, setterFunction: setIterations });

  const handleGrainsPerIterationChange = numericValue =>
    setPositiveInteger({
      value: numericValue,
      setterFunction: setGrainsPerIteration
    });

  return {
    iterations,
    handleIterationsChange,
    grainsPerIteration,
    handleGrainsPerIterationChange,
    loading,
    grid
  };
};

export default useSandPileOptions;
