// Preload script: inject global HTTP proxy for Node.js undici fetch
// Usage: node --import ./proxy-preload.mjs ...
import { EnvHttpProxyAgent, setGlobalDispatcher } from "undici";

const proxy = process.env.HTTPS_PROXY || process.env.HTTP_PROXY;
if (proxy) {
  setGlobalDispatcher(new EnvHttpProxyAgent());
  console.log(`[proxy-preload] Global fetch proxy active: ${proxy}`);
}
