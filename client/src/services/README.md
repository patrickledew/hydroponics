# Hydroponics API Services

This directory contains service files that abstract the interaction with the backend API.

## Overview

The `apiService.ts` file provides a centralized way to interact with the hydroponics backend API. It uses environment variables to configure the API base URL, which makes it easy to switch between development, testing, and production environments.

## Configuration

The API base URL is defined in the `.env` file in the project root as `VITE_API_BASE_URL`. This value should include the protocol, domain/IP, port, and API prefix.

Example:

```
VITE_API_BASE_URL=http://rpi.local:5000/api
```

## Available Services

The `apiService.ts` file provides functions for:

### Moisture Sensor

- `getMoisture()`: Get current moisture level

### Pump Control

- `runPump(speed, duration)`: Run the pump at a specified speed for a specified duration

### Schedule Management

- `getSchedules()`: Get all schedules
- `getSchedule(scheduleId)`: Get a specific schedule by ID
- `createSchedule(schedule)`: Create a new schedule
- `updateSchedule(scheduleId, schedule)`: Update an existing schedule
- `deleteSchedule(scheduleId)`: Delete a schedule
- `activateSchedule(scheduleId)`: Activate a schedule
- `deactivateSchedule(scheduleId)`: Deactivate a schedule
- `triggerSchedule(scheduleId)`: Manually trigger watering for a schedule

## Usage Example

```typescript
import { getMoisture, runPump } from "./services/apiService";

// Get moisture level
const getMoistureData = async () => {
  try {
    const data = await getMoisture();
    console.log(`Current moisture level: ${data.value}`);
  } catch (error) {
    console.error("Failed to get moisture data:", error);
  }
};

// Run pump
const waterPlant = async () => {
  try {
    await runPump(1.0, 5); // Run pump at full speed for 5 seconds
    console.log("Plant watered successfully");
  } catch (error) {
    console.error("Failed to water plant:", error);
  }
};
```
