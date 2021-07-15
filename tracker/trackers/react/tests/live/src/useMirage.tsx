import { createServer } from 'miragejs';
import { useEffect } from 'react';

export function useMirage() {
  useEffect(() => {
    let server = createServer({});
    server.post('/endpoint');
    return () => {
      server.shutdown();
    };
  });
}
