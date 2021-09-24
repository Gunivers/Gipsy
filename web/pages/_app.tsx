import '../styles/globals.css'
import type { AppProps } from 'next/app'
import Layout from '../components/layout'

function GipsyWebserver({ Component, pageProps }: AppProps) {
  return <Component {...pageProps} />
}
export default GipsyWebserver
