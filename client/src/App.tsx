import { useState, useEffect, useMemo } from "react";
import { Chart, type AxisOptions } from "react-charts";
import "./App.css";
import { getMoisture, runPump } from "./services/apiService";

type MoistureDatum = {
  value: number;
  time: Date;
};

type Series = {
  label: string;

  data: MoistureDatum[];
};
function App() {
  const [speed, setSpeed] = useState(1.0);
  const [duration, setDuration] = useState(0.1);
  const [threshold, setThreshold] = useState(0.3);
  const [lastCheck, setLastCheck] = useState(Date.now());

  const [moisture, setMoisture] = useState(0);
  const [moistData, setMoistData] = useState<MoistureDatum[]>([
    { value: 0, time: new Date() },
  ]);

  const data = useMemo((): Series[] => {
    console.log(moistData);
    return [
      {
        label: "Moisture Sensor",
        data: moistData,
      },
      {
        label: "Threshold",
        data: [
          {
            value: threshold,
            time: moistData.sort(
              (a, b) => a.time.getTime() - b.time.getTime()
            )[0].time,
          },
          {
            value: threshold,
            time: new Date(),
          },
        ],
      },
    ];
  }, [moistData, threshold]);

  const primaryAxis = useMemo(
    (): AxisOptions<MoistureDatum> => ({
      getValue: (datum) => datum.time as Date,
    }),
    []
  );

  const secondaryAxes = useMemo(
    (): AxisOptions<MoistureDatum>[] => [
      {
        getValue: (datum) => datum.value,
        min: 0,
        max: 1,
      },
    ],
    []
  );

  const pulse = async () => {
    await runPump(speed, duration);
  };

  const updateMoisture = async () => {
    try {
      const data = await getMoisture();
      setMoisture(data.value);
      setMoistData((moistData) =>
        [
          ...moistData,
          { value: data.value, time: new Date() } as MoistureDatum,
        ].filter((p) => p.time.getTime() > Date.now() - 1000 * 60 * 30)
      );
    } catch {
      console.error("Error fetching moisture sensor reading");
    }
  };

  useEffect(() => {
    const int = setInterval(async () => {
      await updateMoisture();
    }, 100);
    return () => clearInterval(int);
  }, []);

  return (
    <>
      <h1>Hydroponics Controller</h1>
      <button onClick={pulse}>Pulse motor</button>
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "start",
        }}
      >
        <label htmlFor="speed">Speed: {speed}</label>
        <input
          id="speed"
          className={`input-range ${speed < 0 ? "negative" : ""}`}
          type="range"
          min="-1"
          max="1"
          step="0.1"
          value={speed}
          onChange={(e) => setSpeed(parseFloat(e.target.value))}
        />
        <label htmlFor="duration">Duration: {duration}</label>
        <input
          id="duration"
          style={{ width: "100%" }}
          type="range"
          min="0"
          max="5"
          step="0.1"
          value={duration}
          onChange={(e) => setDuration(parseFloat(e.target.value))}
        />
      </div>

      <h2>Moisture Value: {moisture.toFixed(5)}</h2>
      <div className="card chart-container">
        {moistData && (
          <>
            <Chart
              options={{
                data,
                primaryAxis,
                secondaryAxes,
              }}
            />
          </>
        )}
      </div>
      <div className="card">
        <label htmlFor="threshold">Threshold: {threshold}</label>
        <input
          id="threshold"
          style={{ width: "100%" }}
          type="range"
          min="0"
          max="1"
          step="0.01"
          value={threshold}
          onChange={(e) => setThreshold(parseFloat(e.target.value))}
        />
      </div>
    </>
  );
}

export default App;
