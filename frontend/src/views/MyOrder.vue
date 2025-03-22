<template>
    <div>
        <el-card>
            <el-table :data="orderData" stripe style="width: 100%" border>
                <el-table-column prop="oId" label="挂号单号" width="80px"></el-table-column>
                <el-table-column prop="pId" label="本人id" width="75px"></el-table-column>
                <el-table-column prop="pName" label="姓名" width="75px"></el-table-column>
                <el-table-column prop="dId" label="医生id" width="75px"></el-table-column>
                <el-table-column prop="dName" label="医生姓名" width="80px"></el-table-column>

                <el-table-column prop="oStart" label="挂号时间" width="195px"></el-table-column>
                <el-table-column prop="oEnd" label="结束时间" width="185px"></el-table-column>
                <el-table-column prop="oTotalPrice" label="需交费用/元" width="100px"></el-table-column>
                <el-table-column prop="oPriceState" label="缴费状态" width="150px">
                    <template slot-scope="scope">
                        <el-tag type="success" v-if="scope.row.oPriceState === 1">已缴费</el-tag>
                        <el-button type="warning" icon="iconfont icon-r-mark1" style="font-size: 14px" v-if="
                            scope.row.oPriceState === 0 &&
                            scope.row.oState === 1
                        " @click="priceClick(scope.row.oId, scope.row.dId, scope.row.oTotalPrice, scope.row.pName)">
                            点击缴费</el-button>
                    </template>
                </el-table-column>
                <el-table-column prop="oState" label="挂号状态" width="100px">
                    <template slot-scope="scope">
                        <el-tag type="success" v-if="
                            scope.row.oState === 1 &&
                            scope.row.oPriceState === 1
                        ">已完成</el-tag>
                        <el-tag type="danger" v-if="
                            scope.row.oState === 0
                        ">未完成</el-tag>
                    </template>
                </el-table-column>
                <el-table-column label="报告单">
                    <template slot-scope="scope">
                        <el-button type="success" icon="el-icon-search" style="font-size: 14px"
                            @click="seeReport(scope.row.oId)" v-if="
                                scope.row.oState === 1 &&
                                scope.row.oPriceState === 1
                            "> 查看</el-button>
                    </template>
                </el-table-column>
            </el-table>
        </el-card>
        <!-- 评价对话框 -->
        <el-dialog title="用户评价" :visible.sync="starVisible">
            <div>
                <h3>
                    请对工号：{{ dId }}&nbsp;医生：{{ dName }}&nbsp;进行评价
                </h3>
            </div>
            <div>
                <el-rate v-model="star" show-text> </el-rate>
            </div>
            <div slot="footer" class="dialog-footer">
                <el-button @click="starVisible = false" style="font-size: 18px;"><i class="el-icon-close"
                        style="font-size: 20px;"></i> 取 消</el-button>
                <el-button type="primary" @click="starClick" style="font-size: 18px;"><i class="el-icon-check"
                        style="font-size: 20px;"></i> 确 定</el-button>
            </div>
        </el-dialog>
    </div>
</template>
<script>
import request from "@/utils/request.js";
import jwtDecode from "jwt-decode";
import { getToken } from "@/utils/storage.js";
export default {
    name: "MyOrder",
    data() {
        return {
            userId: 1,
            orderData: [],
            star: 5,
            starVisible: false,
            dId: 1,
            dName: "",
        };
    },
    methods: {
        //评价点击确认
        starClick() {
            request
                .get("doctor/updateStar", {
                    params: {
                        dId: this.dId,
                        dStar: this.star,
                    },
                })
                .then((res) => {
                    if (res.data.status !== 200)
                        return this.$message.error("评价失败");
                    this.$message.success(res.data.message);
                    this.starVisible = false;
                });
        },
        //查看报告单
        seeReport(id) {
            window.location.href =
                "http://127.0.0.1:5000/patient/pdf?oId=" + id;
        },
        //点击缴费按钮
        priceClick(oId, dId, oTotalPrice, pName) {
            // 发送 POST 请求到后端
            fetch("http://127.0.0.1:5000/alipay/pay", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    subject: `${pName}就诊费用`,
                    oId: oId,
                    totalAmount: oTotalPrice,
                    passbackParams: "order" //订单支付
                })
            })
                .then(response => response.json())
                .then(data => {
                    if (data.payUrl) {
                        // 在新窗口打开支付宝支付页面
                        window.open(data.payUrl, '_blank', 'width=800,height=600');
                    } else {
                        console.error("支付请求失败:", data);
                    }
                })
                .catch(error => {
                    console.error("网络错误:", error);
                });


            // 设置轮询
            const pollInterval = 5000; // 每5秒查询一次状态
            const pollOrderStatus = setInterval(() => {
                request
                    .get("order/status", {
                        params: {
                            oId: oId,
                        },
                    })
                    .then((res) => {
                        if (res.data.message === "PAID") {
                            clearInterval(pollOrderStatus); // 停止轮询
                            this.$message.success("支付成功！");
                            // 调用其他后续接口，例如更新订单状态和医生信息
                            this.findDoctor(dId);
                        }
                    })
                    .catch((error) => {
                        console.error("查询订单状态出错:", error);
                    });
            }, pollInterval);
        },

        findDoctor(dId) {
            request
                .post("doctor/findDoctorById", {
                    dId: dId
                })
                .then((res) => {
                    if (res.data.status === 200) {
                        this.dId = res.data.data.dId;
                        this.dName = res.data.data.dName;
                        this.starVisible = true; // 显示评价对话框
                        this.requestOrder();  // 刷新订单信息
                    } else {
                        this.$message.error("请求医生数据失败");
                    }
                });
        },

        //请求挂号信息
        requestOrder() {
            request
                .get("patient/findOrderByPid", {
                    params: {
                        pId: this.userId,
                    },
                })
                .then((res) => {
                    console.log(res.data.data);
                    if (res.data.status !== 200) {
                        this.$message.error("请求数据失败");
                    }
                    this.orderData = res.data.data;
                });
        },
    },
    created() {
        //解码token信息
        const token = getToken();
        this.userId = jwtDecode(token).user_id;
        this.userName = jwtDecode(token).user_name;
        this.requestOrder();
        console.log(this.userId)
    },
};
</script>
<style lang="scss" scoped>
.el-dialog div {
    text-align: center;
    margin-bottom: 8px;
}
</style>