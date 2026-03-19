#ifndef REAL_MAP_H
#define REAL_MAP_H

#include <cmath>
#include <nav_msgs/OccupancyGrid.h>
#include <ros/ros.h>
#include <pedsim_msgs/TrackedPersons.h>
#include <visualization_msgs/Marker.h>
#include <spencer_tracking_msgs/TrackedPersons.h>
#include <vector>

#define REAL_MAP_IDX(width, col, row) ((width) * (row) + (col))

struct Point2D {
  double x, y;
};

class RealObstacleProcess {
  public:
    explicit RealObstacleProcess(ros::NodeHandle &nh);
    void YamlReader();
    // callbacks
    void ObstacleCallback(const visualization_msgs::Marker::ConstPtr& walls);
    void PersonsCallback(const pedsim_msgs::TrackedPersons::ConstPtr &msg);

  private:
    ros::NodeHandle &nh_;
    // publishers
    ros::Publisher pub_map_;
    ros::Publisher pub_map_with_people_;

    // subscribers
    ros::Subscriber sub_map_;
    ros::Subscriber sub_tracked_;

    nav_msgs::OccupancyGrid static_map_;
    nav_msgs::OccupancyGrid map_with_people;
    
    bool map_received_ = false;

    std::string frame_id_;
    double resolution_;
    double person_diameter_;
    double xMin, xMax, yMin, yMax;
};

#endif