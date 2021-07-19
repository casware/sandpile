import React, { useEffect } from "react";
import useSandpileVisualizer from "./SandpileVisualizer.hooks";
import CircularProgress from "@material-ui/core/CircularProgress";
import * as d3 from "d3";
const SandpileVisualizer = () => {
  const { grid, loading, error } = useSandpileVisualizer();
  console.log(grid);

  // Set up d3 chart
  useEffect(() => {
    // Do nothing if data is not loaded
    if (loading || error || grid === undefined) {
      return;
    }
    // set the dimensions and margins of the graph
    var margin = { top: 30, right: 30, bottom: 30, left: 30 },
      width = 450 - margin.left - margin.right,
      height = 450 - margin.top - margin.bottom;

    var svg = d3
      .select("#my_dataviz")
      .append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
      .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    // Labels of row and columns
    // Determine row and column names from the values of the items in grid
    const rowNames = [...new Set(grid.map(item => item.row))];
    const columnNames = [...new Set(grid.map(item => item.column))];

    // Build X scales and axis:
    var x = d3.scaleBand().range([0, width]).domain(rowNames).padding(0.01);
    // svg
    //   .append("g")
    //   .attr("transform", "translate(0," + height + ")")
    //   .call(d3.axisBottom(x));

    // Build XY scales and axis:
    var y = d3.scaleBand().range([height, 0]).domain(columnNames).padding(0.01);
    // svg.append("g").call(d3.axisLeft(y));

    // Build color scale
    var myColor = d3.scaleLinear().range(["white", "black"]).domain([0, 4]);

    // Read data from grid
    svg
      .selectAll()
      .data(grid, function (d) {
        return d.row + ":" + d.column;
      })
      .enter()
      .append("rect")
      .attr("x", function (d) {
        return x(d.row);
      })
      .attr("y", function (d) {
        return y(d.column);
      })
      .attr("width", x.bandwidth())
      .attr("height", y.bandwidth())
      .style("fill", function (d) {
        return myColor(d.value);
      });
  }, [grid, loading, error]);

  return (
    <div id="my_dataviz">
      {!loading && !error && grid !== undefined && null}
      {loading && <CircularProgress />}
    </div>
  );
};

export default SandpileVisualizer;
