import { ButtonContext } from './ButtonContext';
import { DeviceContext } from './DeviceContext';
import { ErrorContext } from './ErrorContext';
import { LinkContext } from './LinkContext';
import { OptimizeContext } from './OptimizeContext';
import { TestContext } from './TestContext';
import { WebDocumentContext } from './WebDocumentContext';

export type Context = TestContext | ErrorContext | ButtonContext | LinkContext | OptimizeContext |  WebDocumentContext | DeviceContext;

