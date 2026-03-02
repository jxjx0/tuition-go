'use client'

import { useEffect, useRef, useState } from 'react'

function LoadingSkeleton() {
  return (
    <div className="min-h-screen" style={{ backgroundColor: '#F5F7FA' }}>
      {/* Nav skeleton */}
      <div className="sticky top-0 z-50 border-b" style={{ backgroundColor: '#fff', borderColor: '#E8F0FE' }}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-2.5">
              <div className="w-9 h-9 rounded-lg shimmer" />
              <div className="w-24 h-5 rounded shimmer" />
            </div>
            <div className="hidden md:flex items-center gap-4">
              <div className="w-24 h-8 rounded-lg shimmer" />
              <div className="w-24 h-8 rounded-lg shimmer" />
              <div className="w-24 h-8 rounded-lg shimmer" />
            </div>
            <div className="hidden md:flex items-center gap-3">
              <div className="w-20 h-8 rounded-lg shimmer" />
              <div className="w-28 h-9 rounded-lg shimmer" />
            </div>
          </div>
        </div>
      </div>
      {/* Hero skeleton */}
      <div className="py-20" style={{ background: 'linear-gradient(135deg, #1B3A5C 0%, #4A90D9 100%)' }}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col lg:flex-row items-center gap-12">
            <div className="flex-1 flex flex-col items-center lg:items-start gap-4">
              <div className="w-64 h-8 rounded-full" style={{ backgroundColor: 'rgba(255,255,255,0.15)' }} />
              <div className="w-full max-w-lg h-14 rounded-lg" style={{ backgroundColor: 'rgba(255,255,255,0.1)' }} />
              <div className="w-full max-w-md h-14 rounded-lg" style={{ backgroundColor: 'rgba(255,255,255,0.08)' }} />
              <div className="w-full max-w-sm h-6 rounded" style={{ backgroundColor: 'rgba(255,255,255,0.06)' }} />
              <div className="flex gap-4 mt-4">
                <div className="w-44 h-14 rounded-xl" style={{ backgroundColor: 'rgba(46,170,79,0.6)' }} />
                <div className="w-36 h-14 rounded-xl" style={{ backgroundColor: 'rgba(255,255,255,0.15)' }} />
              </div>
            </div>
            <div className="flex-1 w-full max-w-md">
              <div className="rounded-2xl p-6" style={{ backgroundColor: 'rgba(255,255,255,0.1)', backdropFilter: 'blur(20px)' }}>
                <div className="space-y-4">
                  {[1, 2, 3].map(i => (
                    <div key={i} className="flex items-center gap-4 p-4 rounded-xl bg-white" style={{ opacity: 1 - i * 0.15 }}>
                      <div className="w-12 h-12 rounded-full shimmer" />
                      <div className="flex-1 space-y-2">
                        <div className="w-24 h-4 rounded shimmer" />
                        <div className="w-32 h-3 rounded shimmer" />
                      </div>
                      <div className="space-y-1 text-right">
                        <div className="w-10 h-4 rounded shimmer" />
                        <div className="w-12 h-3 rounded shimmer" />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default function VueBridgePage() {
  const containerRef = useRef<HTMLDivElement>(null)
  const appRef = useRef<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let mounted = true

    async function initVue() {
      if (!containerRef.current || appRef.current) return

      try {
        const { mountVueApp } = await import('../vue-app/mount')
        if (mounted && containerRef.current) {
          appRef.current = mountVueApp(containerRef.current)
          setLoading(false)
        }
      } catch (err) {
        console.error('[v0] Failed to mount Vue app:', err)
        setLoading(false)
      }
    }

    initVue()

    return () => {
      mounted = false
      if (appRef.current) {
        appRef.current.unmount()
        appRef.current = null
      }
    }
  }, [])

  return (
    <>
      {loading && <LoadingSkeleton />}
      <div
        ref={containerRef}
        id="vue-app"
        className="min-h-screen"
        style={{ display: loading ? 'none' : 'block' }}
      />
    </>
  )
}
