#include <pedsim_map/real_map.h>

RealObstacleProcess::RealObstacleProcess(ros::NodeHandle &nh) : nh_(nh) {
  map_received_ = false;
  xMin = 10000;
  xMax = -10000;
  yMin = 10000;
  yMax = -10000;

  pub_map_ = nh_.advertise<nav_msgs::OccupancyGrid>("/map", 1, true);
  pub_map_with_people_ = nh_.advertise<nav_msgs::OccupancyGrid>("/map_with_people", 1, true);
  
  sub_map_ = nh_.subscribe<visualization_msgs::Marker>("/pedsim_visualizer/walls", 1, &RealObstacleProcess::ObstacleCallback, this);
  sub_tracked_ = nh_.subscribe<pedsim_msgs::TrackedPersons>("/tracked_persons", 1, &RealObstacleProcess::PersonsCallback, this);
}

void RealObstacleProcess::YamlReader() {
  nh_.param<std::string>("pedsim_realmap/frame_id", frame_id_, "odom");
  nh_.param<double>("pedsim_realmap/person_diameter", person_diameter_, 0.4);
  nh_.param<double>("pedsim_realmap/resolution", resolution_, 0.1);
}

void RealObstacleProcess::ObstacleCallback(const visualization_msgs::Marker::ConstPtr& walls) {
  if (!map_received_) {
    // 寻找地图的边界
    double px, py;  
    for (const auto& p : walls->points) {
      px = p.x;
      py = p.y;
      if (px < xMin) xMin = px;
      if (px > xMax) xMax = px;
      if (py < yMin) yMin = py;
      if (py > yMax) yMax = py;
    }
    xMin -= 2 * resolution_;
    xMax += 2 * resolution_;
    yMin -= 2 * resolution_;
    yMax += 2 * resolution_;

    int width = ceil((xMax - xMin) / resolution_);
    int height = ceil((yMax - yMin) / resolution_);

    static_map_.info.resolution = resolution_;
    static_map_.info.width = width;
    static_map_.info.height = height;
    static_map_.info.map_load_time = ros::Time::now();

    static_map_.info.origin.position.x = xMin;
    static_map_.info.origin.position.y = yMin;
    static_map_.info.origin.position.z = 0;
    static_map_.info.origin.orientation.x = 0;
    static_map_.info.origin.orientation.y = 0;
    static_map_.info.origin.orientation.z = 0;
    static_map_.info.origin.orientation.w = 1;

    static_map_.header.frame_id = frame_id_;
    static_map_.header.stamp = ros::Time::now();
    
    ROS_INFO("RealMap Read a %d X %d map @ %.3lf m/cell",
              static_map_.info.width,
              static_map_.info.height,
              static_map_.info.resolution);

    static_map_.data.assign(static_map_.info.width * static_map_.info.height, 0);

    // 将障碍物投影到静态地图上
    for (const auto& p : walls->points) {
      for (int i = floor((p.x - 0.05) / resolution_); i <= floor((p.x + 0.05) / resolution_); i++) {
        for (int j = floor((p.y - 0.05) / resolution_); j <= floor((p.y + 0.05) / resolution_); j++) {
          int idx = REAL_MAP_IDX(static_map_.info.width, i - xMin / resolution_, j - yMin / resolution_);
          if (idx >= 0 && idx < static_map_.data.size()) {
            static_map_.data[idx] = 100;
          }
        }
      }
    }
    map_received_ = true;
    pub_map_.publish(static_map_);
  }
}

void RealObstacleProcess::PersonsCallback(const pedsim_msgs::TrackedPersons::ConstPtr &msg) {
  if(map_received_){
    map_with_people = static_map_;
    double temp_x, temp_y;
    // for (const auto& person : msg->tracks) {
    //   temp_x = person.pose.pose.position.x;
    //   temp_y = person.pose.pose.position.y;
    //   float mx = temp_x / resolution_ - xMin / resolution_;
    //   float my = temp_y / resolution_ - yMin / resolution_;
    //   float m_radius = person_diameter_ / resolution_ / 2;
    //   for (int i = floor(mx - m_radius); i < ceil(mx + m_radius); i++) {  
    //     for (int j = floor(my - m_radius); j < ceil(my + m_radius); j++) {  
    //       if (hypot(i - mx, j - my) <= m_radius) {
    //         int idx = REAL_MAP_IDX(map_with_people.info.width, i, j);
    //         if (idx >= 0 && idx < map_with_people.data.size()) {
    //           map_with_people.data[idx] = 100; 
    //         }
    //       }
    //     }
    //   }
    // }
    pub_map_with_people_.publish(map_with_people);
  }
}