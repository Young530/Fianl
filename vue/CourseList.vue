<template>
  <div>
    <el-row>
      <el-col :span="6" v-for="course in courses" :key="course.id">
        <el-card>
          <div slot="header" class="clearfix">
            <span>{{ course.name }}</span>
            <el-button @click="editCourse(course.id)" size="mini" style="float: right;">编辑</el-button>
            <el-button @click="deleteCourse(course.id)" size="mini" style="float: right; margin-right: 5px;">删除</el-button>
          </div>
          <div>{{ course.description }}</div>
          <el-button @click="goToModule(course.id)" size="mini">进入课程</el-button>
        </el-card>
      </el-col>
    </el-row>
    <el-button @click="addCourse" size="small" type="primary">添加课程</el-button>
  </div>
</template>

<script>
import { ElCard, ElButton, ElRow, ElCol } from 'element-ui';
import axios from 'axios';

export default {
  name: 'CourseList',
  components: {
    ElCard,
    ElButton,
    ElRow,
    ElCol
  },
  data() {
    return {
      courses: []
    };
  },
  methods: {
    async fetchCourses() {
      const response = await axios.get('/api/courses');
      this.courses = response.data;
    },
    goToModule(courseId) {
      this.$router.push({ name: 'modules', params: { courseId } });
    },
    async deleteCourse(courseId) {
      await axios.delete(`/api/courses/${courseId}`);
      this.fetchCourses();
    },
    editCourse(courseId) {
      // 打开编辑课程的界面
    },
    addCourse() {
      // 打开添加课程的界面
    }
  },
  mounted() {
    this.fetchCourses();
  }
};
</script>
