<template>
    <div>
        <el-card>
            <el-table :data="bedData" border stripe>
                <el-table-column label="床号" prop="bId" v-model="bedData.bId"></el-table-column>
                <el-table-column label="用户id" prop="pId" v-model="bedData.pId"></el-table-column>
                <el-table-column label="医生id" prop="dId" v-model="bedData.dId"></el-table-column>
                <el-table-column label="原因" prop="bReason" v-model="bedData.bReason"></el-table-column>
                <el-table-column label="开始时间" prop="bStart" v-model="bedData.bStart"></el-table-column>
                <el-table-column label="结束时间" prop="bEnd" v-model="bedData.bEnd"></el-table-column>
            </el-table>
        </el-card>
    </div>
</template>
<script>
import jwtDecode from "jwt-decode";
import request from "@/utils/request.js";
import { getToken } from "@/utils/storage.js";
export default {
    name: "MyBed",
    data() {
        return {
            bedData:[],
            userId:1,
        }
    },
    methods: {
        //请求病床信息
        requestBed(){
            request.get("patient/findBedByPid", {
                params: {
                    pId: this.userId
                }
            })
            .then(res => {
                if(res.data.status !== 200)
                    return this.$message.error("请求数据失败");
                console.log(res.data.data);
                this.bedData = res.data.data;
            })

        },
    },
    created(){
        //解码token信息
        const token = getToken();
        this.userId = jwtDecode(token).user_id;
        this.requestBed();
    }
}
</script>