
#define BOOST_BIND_NO_PLACEHOLDERS

#include "rclcpp/rclcpp.hpp"
#include "inertial_loam/utils/common.hpp"

// #include "geometry_msgs/msg/vector3_stamped.hpp"
// #include <geometry_msgs/msg/pose_with_covariance_stamped.hpp>
#include <sensor_msgs/msg/time_reference.hpp>
#include <sensor_msgs/msg/imu.hpp>


#include <memory>
#include <cstdio>
#include <cmath>
#include <queue>
#include <vector>
#include <Eigen/Core>

using namespace std;
// using namespace Eigen;

using std::placeholders::_1;


class IMUTimeRef : public rclcpp::Node
{
    private:
        rclcpp::CallbackGroup::SharedPtr sub1_cb_group_;
        rclcpp::CallbackGroup::SharedPtr sub2_cb_group_;

        rclcpp::Subscription<sensor_msgs::msg::Imu>::SharedPtr imu_data_sub;
        rclcpp::Subscription<sensor_msgs::msg::TimeReference>::SharedPtr imu_time_sub;
 
        rclcpp::Publisher<sensor_msgs::msg::Imu>::SharedPtr imu_reference_pub;



        double abs_time_zero{}; 
        double ref_time_zero{}; 

        std::string imu_topic_in_{};
        std::string imu_topic_out_{};

        deque<sensor_msgs::msg::Imu::SharedPtr> imu_data_buffer;
        deque<sensor_msgs::msg::TimeReference::SharedPtr> imu_time_buffer;

        int imu_step_delay_;

        bool print_states_{};

        // std_msgs::msg::Header imu_data_header;
        sensor_msgs::msg::Imu current_imu_data;
        sensor_msgs::msg::TimeReference current_imu_time_ref;

    
    
    public:
        IMUTimeRef() // constructer
        : Node("IMUTimeRef")
        {   
                   
            declare_parameter("imu_topic_in", "/imu/data_raw");
            get_parameter("imu_topic_in", imu_topic_in_);
            declare_parameter("imu_topic_out", "/imu/data_raw_time_ref");
            get_parameter("imu_topic_out", imu_topic_out_);

            // declare_parameter("print_states", true);
            // get_parameter("print_states", print_states_);

            RCLCPP_INFO(get_logger(),"Listning on topic %s", imu_topic_in_.c_str());
            RCLCPP_INFO(get_logger(),"Publishing on topic %s", imu_topic_out_.c_str());

        
            // run_cb_group_ = this->create_callback_group(rclcpp::CallbackGroupType::MutuallyExclusive);
            // run_timer = this->create_wall_timer(1000ms, std::bind(&EKF::updateZeroMeasurement, this), run_cb_group_);

            sub1_cb_group_ = this->create_callback_group(rclcpp::CallbackGroupType::MutuallyExclusive);
            rclcpp::SubscriptionOptions options1;
            options1.callback_group = sub1_cb_group_;
            sub2_cb_group_ = this->create_callback_group(rclcpp::CallbackGroupType::MutuallyExclusive);
            rclcpp::SubscriptionOptions options2;
            options2.callback_group = sub2_cb_group_;

            // sub2_cb_group_ = this->create_callback_group(rclcpp::CallbackGroupType::MutuallyExclusive);
            // rclcpp::SubscriptionOptions options2;
            // options2.callback_group = sub2_cb_group_;


            imu_data_sub = this->create_subscription<sensor_msgs::msg::Imu>(imu_topic_in_, 100, std::bind(&IMUTimeRef::imuDataHandler, this, _1), options1);
            imu_time_sub = this->create_subscription<sensor_msgs::msg::TimeReference>("/imu/time_ref", 100, std::bind(&IMUTimeRef::imuTimeHandler, this, _1), options2);
      
            imu_reference_pub = this->create_publisher<sensor_msgs::msg::Imu>(imu_topic_out_, 100);
    

        }
        ~IMUTimeRef(){}


        
        void imuDataHandler(const sensor_msgs::msg::Imu::SharedPtr imu_data)
        {
            if (0.0 == abs_time_zero)
            {
                RCLCPP_INFO_ONCE(get_logger(), "First imu msg recieved..");
                abs_time_zero = toSec(imu_data->header.stamp);
                // int p = 4;
                // abs_time_zero = std::floor(abs_time_zero * pow(float(10),p))/ pow(float(10),p );
                RCLCPP_INFO_ONCE(get_logger(), "abs zero time: %f", abs_time_zero);
                // double micro_sec_abs_time = std::floor(abs_time_zero *1e4);
                // RCLCPP_INFO_ONCE(get_logger(), "abs zero time microsec: %f", micro_sec_abs_time);
                // abs_time_zero = (double)(micro_sec_abs_time * 1e-4);
                // RCLCPP_INFO_ONCE(get_logger(), "abs zero time rounded: %f", abs_time_zero);
                
            }
            // put data into buffer back
            imu_data_buffer.push_back(imu_data);

            correctImuTimeStamp();

        }   


        void imuTimeHandler(const sensor_msgs::msg::TimeReference::SharedPtr imu_time)
        {
            if (0.0 == abs_time_zero)
            {
                RCLCPP_INFO_ONCE(get_logger(), "First time_ref msg recieved..");
                ref_time_zero = toSec(imu_time->time_ref);
            }
            imu_time_buffer.push_back(imu_time);
        }

        
        void correctImuTimeStamp()
        {
            
            for (size_t i=0; i < std::min(imu_data_buffer.size(), imu_time_buffer.size()); i++){
                current_imu_data = *imu_data_buffer.front();
                current_imu_time_ref = *imu_time_buffer.front();

                double imu_data_stamp = toSec(current_imu_data.header.stamp);
                double imu_ref_stamp = toSec(current_imu_time_ref.header.stamp);
                


                if (imu_data_stamp == imu_ref_stamp){
                    // change the timestamp on the data msg accordingly and republish the data message
                    // RCLCPP_INFO(get_logger(), "In-Sync: %f, %f", imu_data_stamp, imu_ref_stamp);

                    double ref_time = toSec(current_imu_time_ref.time_ref);
                    current_imu_data.header.stamp = toHeaderStamp(abs_time_zero + (ref_time - ref_time_zero));

                    imu_reference_pub->publish(current_imu_data);

                    // pop both qeues
                    imu_data_buffer.pop_front();
                    imu_time_buffer.pop_front();
                    continue;
                }

                RCLCPP_INFO(get_logger(), "Not Synced: %f, %f, diff %f", imu_data_stamp, imu_ref_stamp, imu_data_stamp - imu_ref_stamp);
                // hope not to handle mismatches
                if (imu_data_stamp > imu_ref_stamp){
                    imu_time_buffer.pop_front();
                    correctImuTimeStamp();
                    // continue;
                }
                else if (imu_data_stamp < imu_ref_stamp){
                    imu_data_buffer.pop_front();
                    correctImuTimeStamp();
                    // continue;
                }
            }
        }


};

int main(int argc, char * argv[])
{
    rclcpp::init(argc, argv);
    auto ekf_node = std::make_shared<IMUTimeRef>();
    rclcpp::executors::MultiThreadedExecutor executor;
    executor.add_node(ekf_node);
    
    executor.spin();
    rclcpp::shutdown();
    return 0;
}