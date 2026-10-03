"use client";

import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
// import { ExternalLink, Clock, User, CheckCircle, AlertCircle, FileText, Award } from "lucide-react";
import { Button } from "@/components/ui/primitives";

// Activity event type
export type ActivityEvent = {
  id: string;
  type: "ResidentJoined" | "TaskPublished" | "ContributionSubmitted" | "SubmissionApproved" | "ReputationGranted";
  timestamp: string;
  publicData: {
    shortId?: string;
    displayName?: string;
    taskId?: string;
    taskTitle?: string;
    submissionId?: string;
    points?: number;
    evidenceType?: string;
  };
};

// Activity feed props
interface ActivityFeedProps {
  limit?: number;
  className?: string;
}

// Icon mapping for event types
const eventIcons = {
  ResidentJoined: User,
  TaskPublished: FileText,
  ContributionSubmitted: AlertCircle,
  SubmissionApproved: CheckCircle,
  ReputationGranted: Award,
};

// Color mapping for event types
const eventColors = {
  ResidentJoined: "text-blue-600 bg-blue-50 border-blue-200",
  TaskPublished: "text-green-600 bg-green-50 border-green-200",
  ContributionSubmitted: "text-orange-600 bg-orange-50 border-orange-200",
  SubmissionApproved: "text-green-600 bg-green-50 border-green-200",
  ReputationGranted: "text-purple-600 bg-purple-50 border-purple-200",
};

// Format timestamp
const formatTimestamp = (timestamp: string) => {
  const date = new Date(timestamp);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / (1000 * 60));
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffMins < 1) return "Just now";
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;

  return date.toLocaleDateString();
};

// Event display component
const EventItem = ({ event }: { event: ActivityEvent }) => {
  const IconComponent = eventIcons[event.type];
  const colorClass = eventColors[event.type];

  return (
    <div className="flex gap-3 p-4 hover:bg-gray-50 transition-colors">
      <div className={`p-2 rounded-lg border ${colorClass}`}>
        <IconComponent className="h-4 w-4" />
      </div>

      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between gap-2">
          <div className="flex-1">
            {/* Event type and title */}
            <p className="text-sm font-medium text-gray-900 mb-1">
              {getEventTitle(event)}
            </p>

            {/* Event details */}
            <p className="text-sm text-gray-600">
              {getEventDescription(event)}
            </p>

            {/* Additional details based on type */}
            {event.type === "ResidentJoined" && (
              <p className="text-xs text-gray-500 mt-1">
                Joined MOOD Network
              </p>
            )}

            {event.type === "TaskPublished" && (
              <p className="text-xs text-gray-500 mt-1">
                Task: {event.publicData.taskTitle}
              </p>
            )}

            {event.type === "ContributionSubmitted" && (
              <div className="mt-1">
                <p className="text-xs text-gray-500">
                  Task: {event.publicData.taskTitle}
                </p>
                <p className="text-xs text-gray-500">
                  Submitted by {event.publicData.displayName}
                </p>
              </div>
            )}

            {event.type === "SubmissionApproved" && (
              <div className="mt-1">
                <p className="text-xs text-gray-500">
                  Task: {event.publicData.taskTitle}
                </p>
                <p className="text-xs text-gray-500">
                  Approved for {event.publicData.displayName}
                </p>
              </div>
            )}

            {event.type === "ReputationGranted" && (
              <div className="mt-1">
                <p className="text-xs text-gray-500">
                  +{event.publicData.points} reputation points
                </p>
                <p className="text-xs text-gray-500">
                  Evidence: {event.publicData.evidenceType}
                </p>
              </div>
            )}
          </div>

          <div className="flex flex-col items-end gap-1 flex-shrink-0">
            <span className="text-xs text-gray-500">
              {formatTimestamp(event.timestamp)}
            </span>
            {event.type === "TaskPublished" && (
              <Button
                variant="ghost"
                size="sm"
                className="text-xs h-6"
                onClick={() => {
                  window.open(`/tasks/${event.publicData.taskId}`, "_blank");
                }}
              >
                View
                <ExternalLink className="h-3 w-3 ml-1" />
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

// Get event title
const getEventTitle = (event: ActivityEvent) => {
  switch (event.type) {
    case "ResidentJoined":
      return "New Resident Joined";
    case "TaskPublished":
      return "Task Published";
    case "ContributionSubmitted":
      return "Contribution Submitted";
    case "SubmissionApproved":
      return "Contribution Approved";
    case "ReputationGranted":
      return "Reputation Granted";
    default:
      return "Network Activity";
  }
};

// Get event description
const getEventDescription = (event: ActivityEvent) => {
  switch (event.type) {
    case "ResidentJoined":
      return `Resident ${event.publicData.displayName} (${event.publicData.shortId}) joined the network`;
    case "TaskPublished":
      return `New task "${event.publicData.taskTitle}" opened for contributions`;
    case "ContributionSubmitted":
      return `New submission for task "${event.publicData.taskTitle}"`;
    case "SubmissionApproved":
      return `Contribution for task "${event.publicData.taskTitle}" approved`;
    case "ReputationGranted":
      return `Awarded ${event.publicData.points} reputation points`;
    default:
      return "Network event";
  }
};

export default function ActivityFeed({ limit = 20, className = "" }: ActivityFeedProps) {
  const [events, setEvents] = useState<ActivityEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [hasMore, setHasMore] = useState(true);
  const [offset, setOffset] = useState(0);

  const fetchEvents = async (newOffset = 0) => {
    try {
      const response = await fetch(`/api/network/activity?limit=${limit}&offset=${newOffset}`);
      const data = await response.json();

      if (newOffset === 0) {
        setEvents(data.events);
      } else {
        setEvents(prev => [...prev, ...data.events]);
      }

      setHasMore(newOffset + data.events.length < data.total);
      setLoading(false);
    } catch (error) {
      console.error("Failed to fetch activity events:", error);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEvents();
  }, []);

  const loadMore = () => {
    if (!loading && hasMore) {
      const newOffset = offset + limit;
      setOffset(newOffset);
      fetchEvents(newOffset);
    }
  };

  if (loading && events.length === 0) {
    return (
      <Card className={`p-6 ${className}`}>
        <h2 className="text-lg font-semibold mb-4">Network Activity</h2>
        <div className="space-y-3">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="flex gap-3">
              <Skeleton className="h-8 w-8 rounded" />
              <div className="flex-1 space-y-2">
                <Skeleton className="h-4 w-48" />
                <Skeleton className="h-3 w-64" />
              </div>
            </div>
          ))}
        </div>
      </Card>
    );
  }

  return (
    <Card className={`p-6 ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold">Network Activity</h2>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => fetchEvents()}
          disabled={loading}
        >
          {loading ? "Refreshing..." : "Refresh"}
        </Button>
      </div>

      <div className="space-y-1">
        {events.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <Clock className="h-8 w-8 mx-auto mb-2" />
            <p>No recent activity</p>
          </div>
        ) : (
          <>
            {events.map((event) => (
              <EventItem key={event.id} event={event} />
            ))}

            {hasMore && (
              <div className="pt-4 border-t">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={loadMore}
                  disabled={loading}
                  className="w-full"
                >
                  {loading ? "Loading..." : "Load more"}
                </Button>
              </div>
            )}
          </>
        )}
      </div>
    </Card>
  );
}