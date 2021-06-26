import logo from "../static/logo.svg";
import SandpileOptions from "components/SandpileOptions/index";
import SandpileVisualizer from "components/SandpileVisualizer/index";
import Grid from "@material-ui/core/Grid";
import Typography from "@material-ui/core/Typography";
function App() {
  return (
    <div className="App">
      <Grid
        container
        direction="column"
        alignItems="center"
        sm={12}
        justify="center"
      >
        <Grid item>
          <Typography variant="h1" color="textPrimary">
            Grains of Sand
          </Typography>
        </Grid>
        <Grid item>
          <Typography variant="h3" color="textSecondary">
            Bak-Tang-Wiesenfeld Model of Criticality
          </Typography>
        </Grid>
        <Grid item>
          <SandpileOptions />
        </Grid>
        <Grid item>
          <SandpileVisualizer />
        </Grid>
      </Grid>
    </div>
  );
}

export default App;
