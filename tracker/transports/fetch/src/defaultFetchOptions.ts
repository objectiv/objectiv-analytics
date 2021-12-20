/*
 * Copyright 2021 Objectiv B.V.
 */

/**
 * The default set of options for the fetch API call.
 * The `body` parameter is internally managed and should not be overridden.
 */
export const defaultFetchOptions: Omit<RequestInit, 'body'> = {
  method: 'POST',
  mode: 'cors',
  headers: {
    'Content-Type': 'text/plain',
  },
  credentials: 'include',
};
