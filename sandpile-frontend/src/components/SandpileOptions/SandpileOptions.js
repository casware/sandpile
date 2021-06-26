import React from "react";

// Material-ui
import Grid from "@material-ui/core/Grid";
import TextField from "@material-ui/core/TextField";
import makeStyles from "@material-ui/core/styles/makeStyles";
import Button from "@material-ui/core/Button";

// Hooks for state
import usingSandpileOptions from "./SandpileOptions.hooks";

const styles = {
  textfield: {
    margin: "2rem",
    padding: ".5rem"
  },
  grains: {
    width: "8rem",
    margin: "2rem",
    padding: ".5rem"
  }
};

const useStyles = makeStyles(styles);

const SandpileOptions = props => {
  const {
    iterations,
    handleIterationsChange,
    grainsPerIteration,
    handleGrainsPerIterationChange,
    loading,
    grid
  } = usingSandpileOptions();

  const classes = useStyles();
  return (
    <Grid container direction="row" alignItems="center" spacing={2}>
      <Grid item>
        <TextField
          className={classes.textfield}
          name="iterations"
          variant="outlined"
          onChange={event => handleIterationsChange(Number(event.target.value))}
          label="Iterations"
          value={iterations}
        />
      </Grid>
      <Grid item>
        <TextField
          variant="outlined"
          className={classes.grains}
          name="grains-per-step"
          onChange={event => handleGrainsPerIterationChange(event.target.value)}
          label="Grains per Step"
          value={grainsPerIteration}
        />
      </Grid>
      <Grid item>
        <Button variant="contained" color="primary">
          Start
        </Button>
      </Grid>
      <Grid item>
        <Button variant="contained" color="primary">
          Stop
        </Button>
      </Grid>
    </Grid>
  );
};

export default SandpileOptions;
