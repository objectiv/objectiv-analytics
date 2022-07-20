/*
 * Copyright 2021-2022 Objectiv B.V.
 */

export const UUIDV4_REGEX = /^[0-9A-F]{8}-[0-9A-F]{4}-[4][0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12}$/i;

export const matchUUID = expect.stringMatching(UUIDV4_REGEX);
