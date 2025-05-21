import React from 'react';

const ObjectDisplay = ({ results }) => {
  // Return if no results
  if (!results || !results.summary) {
    return null;
  }

  // Extract data
  const { summary, total_frames, processed_frames, duration, avg_processing_time } = results;
  const { total_detections, class_counts } = summary;

  // Sort class counts by count (descending)
  const sortedClasses = Object.entries(class_counts).sort((a, b) => b[1] - a[1]);

  // Calculate stats
  const fps = processed_frames / duration;
  const avgObjectsPerFrame = total_detections / processed_frames;

  return (
    <div className="card">
      <h2 className="text-xl font-bold mb-4">Detection Results</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <div className="bg-gray-100 p-4 rounded-md">
          <div className="text-sm font-semibold text-gray-500">Total Detections</div>
          <div className="text-3xl font-bold">{total_detections}</div>
        </div>
        <div className="bg-gray-100 p-4 rounded-md">
          <div className="text-sm font-semibold text-gray-500">Objects Per Frame (avg)</div>
          <div className="text-3xl font-bold">{avgObjectsPerFrame.toFixed(2)}</div>
        </div>
        <div className="bg-gray-100 p-4 rounded-md">
          <div className="text-sm font-semibold text-gray-500">Processing Time</div>
          <div className="text-3xl font-bold">{avg_processing_time.toFixed(3)}s</div>
        </div>
        <div className="bg-gray-100 p-4 rounded-md">
          <div className="text-sm font-semibold text-gray-500">Video Duration</div>
          <div className="text-3xl font-bold">{duration.toFixed(2)}s</div>
        </div>
      </div>

      <h3 className="text-lg font-semibold mb-3">Detected Objects</h3>
      <div className="bg-white border border-gray-200 rounded-md overflow-hidden mb-6">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Object Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Count
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Percentage
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {sortedClasses.map(([className, count], index) => (
                <tr key={index} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {className}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {count}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {((count / total_detections) * 100).toFixed(1)}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {results.output_video && (
        <div>
          <h3 className="text-lg font-semibold mb-3">Processed Video</h3>
          <p className="text-sm text-gray-600 mb-2">
            The processed video with object detection is available for download.
          </p>
          <a
            href={`/api/video/${results.analysis_id}`}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-block bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
          >
            Download Processed Video
          </a>
        </div>
      )}
    </div>
  );
};

export default ObjectDisplay;