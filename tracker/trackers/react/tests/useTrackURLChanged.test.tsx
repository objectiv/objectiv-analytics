import { render } from '@testing-library/react';
import { renderHook } from '@testing-library/react-hooks';
//import { renderHook } from '@testing-library/react-hooks';
import { useEffect } from 'react';
import { ReactTracker, TrackerContextProvider } from '../src';
import { useTrackURLChanged } from '../src/useTrackURLChanged';

const oldWindowLocation = window.location;

beforeAll(() => {
  window.location = Object.defineProperties(
    {},
    {
      ...Object.getOwnPropertyDescriptors(oldWindowLocation),
      href: {
        configurable: true,
      },
    }
  );
});
afterAll(() => {
  // restore `window.location` to the original `jsdom`
  // `Location` object
  window.location = oldWindowLocation;
});

describe('useTrackURLChanged', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  const spyTransport = {
    transportName: 'SpyTransport',
    handle: jest.fn(),
    isUsable: () => true,
  };

  const renderSpy = jest.fn();

  const tracker = new ReactTracker({ transport: spyTransport });

  const Index = () => {
    return (
      <TrackerContextProvider tracker={tracker}>
        <Application />
      </TrackerContextProvider>
    );
  };

  const Application = () => {
    useTrackURLChanged();

    useEffect(renderSpy);

    return <>Test application</>;
  };

  it('should execute on mount', () => {
    render(<Index />);

    // TODO JSDOM doesn't support mocking location out of the box
  });

  it('should allow overriding the tracker with a custom one', () => {
    const spyTransport2 = {
      transportName: 'spyTransport2',
      handle: jest.fn(),
      isUsable: () => true,
    };
    const anotherTracker = new ReactTracker({ transport: spyTransport2 });
    renderHook(() => useTrackURLChanged(anotherTracker));

    // TODO JSDOM doesn't support mocking location out of the box
  });
});
