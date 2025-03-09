/**
 * Timezone Utility Functions
 * 
 * This file contains utility functions for handling timezone conversions,
 * particularly between New York time and UTC, accounting for Daylight Saving Time.
 */

/**
 * Determines if a given date is in Daylight Saving Time for US Eastern Time.
 * 
 * For US Eastern Time, DST starts on the second Sunday in March and ends on the first Sunday in November.
 * 
 * @param date The date to check
 * @returns True if the date is in DST, False otherwise
 */
export function isDstInEasternTime(date: Date): boolean {
  // Get year from the date
  const year = date.getFullYear();
  
  // DST starts on the second Sunday in March at 2 AM
  let marchDate = new Date(year, 2, 1); // March is month 2 (0-indexed)
  // Find the first Sunday in March
  while (marchDate.getDay() !== 0) { // 0 is Sunday
    marchDate.setDate(marchDate.getDate() + 1);
  }
  // Find the second Sunday in March
  const dstStart = new Date(marchDate);
  dstStart.setDate(dstStart.getDate() + 7);
  dstStart.setHours(2, 0, 0, 0);
  
  // DST ends on the first Sunday in November at 2 AM
  let novemberDate = new Date(year, 10, 1); // November is month 10 (0-indexed)
  // Find the first Sunday in November
  while (novemberDate.getDay() !== 0) { // 0 is Sunday
    novemberDate.setDate(novemberDate.getDate() + 1);
  }
  const dstEnd = new Date(novemberDate);
  dstEnd.setHours(2, 0, 0, 0);
  
  // Check if the date is within DST period
  const isDst = date >= dstStart && date < dstEnd;
  
  // Format dates for logging
  const formatDate = (d: Date) => {
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`;
  };
  
  console.log(`DST Check for ${formatDate(date)}:
    Year: ${year}
    DST Start: ${formatDate(dstStart)} (Second Sunday in March at 2 AM)
    DST End: ${formatDate(dstEnd)} (First Sunday in November at 2 AM)
    Is date >= DST Start: ${date >= dstStart ? "Yes" : "No"}
    Is date < DST End: ${date < dstEnd ? "Yes" : "No"}
    Is in DST: ${isDst ? "Yes" : "No"}
  `);
  
  return isDst;
}

/**
 * Converts New York time to UTC.
 * 
 * @param date The date in New York time
 * @returns The date in UTC
 */
export function nyToUtc(date: Date): Date {
  // Create a new date object to avoid modifying the original
  const newDate = new Date(date);
  
  // Check if the date is in DST
  const isDst = isDstInEasternTime(newDate);
  
  // Apply the offset
  // During DST, New York is UTC-4, otherwise it's UTC-5
  const utcOffset = isDst ? 4 : 5;
  newDate.setHours(newDate.getHours() + utcOffset);
  
  console.log(`Converting NY time to UTC: 
    Original (NY): ${date.toString()}
    Is DST: ${isDst ? "Yes" : "No"}
    Offset applied: +${utcOffset} hours
    Result (UTC): ${newDate.toString()}
  `);
  
  return newDate;
}

/**
 * Converts UTC to New York time.
 * 
 * @param date The date in UTC
 * @returns The date in New York time
 */
export function utcToNy(date: Date): Date {
  // Create a new date object to avoid modifying the original
  const newDate = new Date(date);
  
  // Try both DST and non-DST offsets to find the correct one
  // This is necessary because we don't know if the UTC time corresponds to DST or not in NY
  
  // Try non-DST first (UTC-5)
  // To convert from UTC to NY during standard time, we SUBTRACT 5 hours
  const nyTimeNonDst = new Date(newDate);
  nyTimeNonDst.setHours(nyTimeNonDst.getHours() - 5);
  
  // Check if this NY time would be in DST
  const isDst = isDstInEasternTime(nyTimeNonDst);
  
  // Apply the correct offset based on DST
  // During DST, New York is UTC-4, otherwise it's UTC-5
  const utcOffset = isDst ? 4 : 5;
  const result = new Date(newDate);
  result.setHours(result.getHours() - utcOffset);
  
  console.log(`Converting UTC to NY time: 
    Original (UTC): ${date.toString()}
    Is DST in NY: ${isDst ? "Yes" : "No"}
    Offset applied: -${utcOffset} hours
    Result (NY): ${result.toString()}
  `);
  
  return result;
}

/**
 * Formats a date object as a string.
 * 
 * @param date The date to format
 * @param includeTimezone Whether to include the timezone in the output
 * @returns The formatted date string
 */
export function formatDateTime(date: Date, includeTimezone: boolean = false): string {
  // Format the date as YYYY-MM-DD HH:MM
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  
  let formatted = `${year}-${month}-${day} ${hours}:${minutes}`;
  
  if (includeTimezone) {
    const isDst = isDstInEasternTime(date);
    const tz = isDst ? "EDT" : "EST";
    formatted += ` ${tz}`;
  }
  
  return formatted;
}

/**
 * Test function to verify time conversion is working correctly
 */
export function testTimeConversion() {
  // Test with current time
  const now = new Date();
  console.log("=== Testing with current time ===");
  console.log("Current local time:", now.toString());
  console.log("Current time ISO:", now.toISOString());
  
  // Test NY to UTC conversion
  const nowAsNY = new Date(now);
  const nowAsUTC = nyToUtc(nowAsNY);
  console.log("Treating current time as NY and converting to UTC:");
  console.log("Original (treated as NY):", nowAsNY.toString());
  console.log("Converted to UTC:", nowAsUTC.toString());
  console.log("Difference in hours:", (nowAsUTC.getTime() - nowAsNY.getTime()) / (1000 * 60 * 60));
  
  // Test UTC to NY conversion
  const nowAsUTC2 = new Date(now);
  const backToNY = utcToNy(nowAsUTC2);
  console.log("Treating current time as UTC and converting to NY:");
  console.log("Original (treated as UTC):", nowAsUTC2.toString());
  console.log("Converted to NY:", backToNY.toString());
  console.log("Difference in hours:", (nowAsUTC2.getTime() - backToNY.getTime()) / (1000 * 60 * 60));
  
  // Test with a specific date in the future
  const futureDate = new Date();
  futureDate.setDate(futureDate.getDate() + 1); // Tomorrow
  futureDate.setHours(14, 0, 0, 0); // 2 PM
  
  console.log("\n=== Testing with future date ===");
  console.log("Future date (local):", futureDate.toString());
  
  // Test NY to UTC conversion with future date
  const futureDateAsNY = new Date(futureDate);
  const futureDateAsUTC = nyToUtc(futureDateAsNY);
  console.log("Treating future date as NY and converting to UTC:");
  console.log("Original (treated as NY):", futureDateAsNY.toString());
  console.log("Converted to UTC:", futureDateAsUTC.toString());
  console.log("Difference in hours:", (futureDateAsUTC.getTime() - futureDateAsNY.getTime()) / (1000 * 60 * 60));
  
  // Test round trip conversion
  const backToNY2 = utcToNy(futureDateAsUTC);
  console.log("Converting back to NY:");
  console.log("UTC:", futureDateAsUTC.toString());
  console.log("Back to NY:", backToNY2.toString());
  console.log("Matches original NY time:", 
    futureDateAsNY.getTime() === backToNY2.getTime() ? "Yes" : "No");
} 