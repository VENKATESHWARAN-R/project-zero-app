import Loading from '@/components/ui/Loading'

export default function LoadingPage() {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center items-center">
      <div className="text-center">
        <Loading />
        <h2 className="text-xl font-semibold text-gray-700 mt-4">Loading...</h2>
        <p className="text-gray-500 mt-2">Please wait while we prepare your content</p>
      </div>
    </div>
  )
}