// Optional sandbox fallback. Production and CI use native PostgreSQL via Compose.
import { mkdirSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { PGlite } from '@electric-sql/pglite'
import { PGLiteSocketServer } from '@electric-sql/pglite-socket'
const path = resolve(process.env.PGLITE_DATA || '../../work/pglite')
mkdirSync(dirname(path), {recursive:true})
const db = await PGlite.create(path)
const server = new PGLiteSocketServer({db,port:Number(process.env.PGPORT||55432),host:'127.0.0.1'})
await server.start()
console.log('PGlite PostgreSQL engine on 127.0.0.1:'+ (process.env.PGPORT||55432))
for(const signal of ['SIGINT','SIGTERM']) process.on(signal,async()=>{await server.stop();await db.close();process.exit(0)})
