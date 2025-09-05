import { useState, useEffect, useMemo } from "react";
import { Chart } from "react-charts";
import reactLogo from "./assets/react.svg";
import viteLogo from "/vite.svg";
import "./App.css";

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
            time: moistData.sort((a, b) => a - b)[0].time,
          },
          {
            value: threshold,
            time: new Date(),
          },
        ],
      },
    ];
  }, [moistData]);

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
    await fetch(`http://rpi.local:5000/pump/${speed}/${duration}`);
  };

  const updateMoisture = async () => {
    try {
      const res = await fetch(`http://rpi.local:5000/moisture`);
      const data = await res.json();
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

  useEffect(() => {
    (async () => {
      if (lastCheck > Date.now() - 10000) return;
      console.log("checking");
      setLastCheck(Date.now());
      if (moistData[moistData.length - 1].value < threshold) {
        await fetch(`http://rpi.local:5000/pump/${1}/${5}`);
      }
    })();
  }, [moistData, threshold]);

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
        <label for="speed">Speed: {speed}</label>
        <input
          id="speed"
          style={{ width: "100%", accentColor: speed < 0 ? "red" : "blue" }}
          type="range"
          min="-1"
          max="1"
          step="0.1"
          value={speed}
          onChange={(e) => setSpeed(e.target.value)}
        />
        <label for="duration">Duration: {duration}</label>
        <input
          id="duration"
          style={{ width: "100%" }}
          type="range"
          min="0"
          max="5"
          step="0.1"
          value={duration}
          onChange={(e) => setDuration(e.target.value)}
        />
      </div>

      <h2>Moisture Value: {moisture.toFixed(5)}</h2>
      <div class="card" style={{ width: 1000, height: 500 }}>
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
      <div class="card">
        <label for="threshold">Threshold: {threshold}</label>
        <input
          id="threshold"
          style={{ width: "100%" }}
          type="range"
          min="0"
          max="1"
          step="0.01"
          value={threshold}
          onChange={(e) => setThreshold(e.target.value)}
        />
      </div>
    </>
  );
}

export default App;
