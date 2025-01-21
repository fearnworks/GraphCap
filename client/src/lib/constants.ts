

// export const POSTGRES_URL = "postgresql://postgres:postgres@localhost:45432/postgres";

import * as dotenv from "dotenv";
dotenv.config();

function getEnvironmentVariable(environmentVariable: string): string {
  const validEnvironmentVariable = process.env[environmentVariable];
  if (!validEnvironmentVariable) {
    throw new Error(`Couldn't find environment variable: ${environmentVariable}`);
  }
  return validEnvironmentVariable;
}

export const ENV = {
  POSTGRES_URL: getEnvironmentVariable("POSTGRES_URL"),
  API_URL: getEnvironmentVariable("API_URL"),
  WORKSPACE: getEnvironmentVariable("WORKSPACE"),
  DATABASE_URL: getEnvironmentVariable("DATABASE_URL"),
  DB_HOST: getEnvironmentVariable("DB_HOST"),
  DB_USER: getEnvironmentVariable("DB_USER"),
  DB_PASSWORD: getEnvironmentVariable("DB_PASSWORD"),
  DB_NAME: getEnvironmentVariable("DB_NAME"),
  DB_PORT: getEnvironmentVariable("DB_PORT"),
};

export const API_URL = ENV.API_URL
export const POSTGRES_URL = ENV.POSTGRES_URL
export const WORKSPACE = ENV.WORKSPACE
export const DATABASE_URL = ENV.DATABASE_URL
export const DB_HOST = ENV.DB_HOST
export const DB_USER = ENV.DB_USER
export const DB_PASSWORD = ENV.DB_PASSWORD
export const DB_NAME = ENV.DB_NAME
export const DB_PORT = ENV.DB_PORT

console.log(ENV)