/**
 * API service for interacting with the hydroponics backend
 */

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:5000/api";

/**
 * Get moisture level from sensor
 * @returns {Promise<{value: number}>} The moisture level
 */
export const getMoisture = async (): Promise<{ value: number }> => {
  const response = await fetch(`${API_BASE_URL}/moisture`);
  return await response.json();
};

/**
 * Run the pump for a specified duration at a specified speed
 * @param {number} speed - Speed of the pump (-1 to 1)
 * @param {number} duration - Duration in seconds
 * @returns {Promise<Response>} Response from the API
 */
export const runPump = async (
  speed: number,
  duration: number
): Promise<Response> => {
  return await fetch(`${API_BASE_URL}/pump/${speed}/${duration}`);
};

/**
 * Get all watering schedules
 * @returns {Promise<Array>} Array of schedule objects
 */
export const getSchedules = async () => {
  const response = await fetch(`${API_BASE_URL}/schedules`);
  return await response.json();
};

/**
 * Get a specific schedule by ID
 * @param {string} scheduleId - ID of the schedule
 * @returns {Promise<Object>} Schedule object
 */
export const getSchedule = async (scheduleId: string) => {
  const response = await fetch(`${API_BASE_URL}/schedules/${scheduleId}`);
  return await response.json();
};

/**
 * Interface for Schedule objects
 */
export interface Schedule {
  id?: string;
  plant_name: string;
  active?: boolean;
  schedule_times: string[];
  days_of_week: number[];
  moisture_threshold?: number;
  check_interval_minutes?: number;
  pump_duration_seconds?: number;
  last_watered?: string | null;
}

/**
 * Create a new schedule
 * @param {Schedule} schedule - Schedule data
 * @returns {Promise<Schedule>} Created schedule
 */
export const createSchedule = async (schedule: Schedule) => {
  const response = await fetch(`${API_BASE_URL}/schedules`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(schedule),
  });
  return await response.json();
};

/**
 * Update an existing schedule
 * @param {string} scheduleId - ID of the schedule to update
 * @param {Schedule} schedule - Updated schedule data
 * @returns {Promise<Schedule>} Updated schedule
 */
export const updateSchedule = async (
  scheduleId: string,
  schedule: Schedule
) => {
  const response = await fetch(`${API_BASE_URL}/schedules/${scheduleId}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(schedule),
  });
  return await response.json();
};

/**
 * Delete a schedule
 * @param {string} scheduleId - ID of the schedule to delete
 * @returns {Promise<{success: boolean}>} Success indicator
 */
export const deleteSchedule = async (scheduleId: string) => {
  const response = await fetch(`${API_BASE_URL}/schedules/${scheduleId}`, {
    method: "DELETE",
  });
  return await response.json();
};

/**
 * Activate a schedule
 * @param {string} scheduleId - ID of the schedule to activate
 * @returns {Promise<{success: boolean}>} Success indicator
 */
export const activateSchedule = async (scheduleId: string) => {
  const response = await fetch(
    `${API_BASE_URL}/schedules/${scheduleId}/activate`,
    {
      method: "PUT",
    }
  );
  return await response.json();
};

/**
 * Deactivate a schedule
 * @param {string} scheduleId - ID of the schedule to deactivate
 * @returns {Promise<{success: boolean}>} Success indicator
 */
export const deactivateSchedule = async (scheduleId: string) => {
  const response = await fetch(
    `${API_BASE_URL}/schedules/${scheduleId}/deactivate`,
    {
      method: "PUT",
    }
  );
  return await response.json();
};

/**
 * Manually trigger watering for a schedule
 * @param {string} scheduleId - ID of the schedule to trigger
 * @returns {Promise<{success: boolean}>} Success indicator
 */
export const triggerSchedule = async (scheduleId: string) => {
  const response = await fetch(
    `${API_BASE_URL}/schedules/${scheduleId}/trigger`,
    {
      method: "POST",
    }
  );
  return await response.json();
};
