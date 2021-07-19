import React, { useState, useEffect } from "react";
import axios from "axios";

const useSandpileVisualizer = params => {
  const [grid, setGrid] = useState(undefined);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);
  const [fetched, setFetched] = useState(false);
  const url = "http://localhost:5000/plots";

  // Transform a 2D array into a flat array composed of objects with column, row, value
  // attributes where row is the index of the outer array and column is the index of the
  // inner array element corresponding to the element at [row][column]
  const transformNestedArray = nested => {
    return nested
      .map((innerArray, outerIndex) => {
        return innerArray.map((item, innerIndex) => ({
          value: item,
          row: outerIndex,
          column: innerIndex
        }));
      })
      .reduce((accum, current) => accum.concat(current));
  };

  const fetchVisualization = async () => {
    try {
      if (
        fetched === true ||
        grid !== undefined ||
        loading === true ||
        error === true
      ) {
        return;
      }
      setLoading(true);
      const result = await axios.get(url);
      console.log(result);
      setGrid(transformNestedArray(result.data));
      setFetched(true);

      setLoading(false);
    } catch (error) {
      console.log(error);
      alert("Error occured while fetching data");
      setError(true);
      setLoading(false);
      setFetched(true);
    }
  };

  // Fetch visualization image
  useEffect(() => {
    if (grid === undefined && loading !== true) {
      fetchVisualization();
    }
  }, [grid, loading, error]);

  return { grid, loading, error };
};

export default useSandpileVisualizer;
