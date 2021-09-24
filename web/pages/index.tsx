import type { NextPage } from 'next'
import Head from 'next/head'
import Image from 'next/image'
import styles from '../styles/Home.module.css'

const Home: NextPage = () => {
  return (
    <div>
      <Head>
        <title>Gipsy Webserver</title>
        <meta name="description" content="Gipsy webserver" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main>
        <h1>Gipsy Web server</h1>
      </main>
    </div>
  )
}

export default Home
