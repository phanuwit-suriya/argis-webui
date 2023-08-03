<template>
  <div>
    <b-container style="padding: 50px 100px 0px 100px" fluid>
      <b-form @submit="onSubmit" @reset="onReset">
        <b-row>
          <b-col>
            <b-form-group
              label-cols-sm="4"
              label-cols-lg="3"
              description="Endpoint URL (e.g., https://compass.thomsonreuters.com/api/monitor/metrics/production/render)"
              label="Enter Endpoint"
              label-for="input-endpoint"
            >
              <b-form-input
                v-model="form.endpoint"
                id="input-endpoint"
                required
                @keydown.enter.exact.prevent
              ></b-form-input>
            </b-form-group>
          </b-col>
        </b-row>
        <b-row>
          <b-col>
            <b-form-group
              label-cols-sm="4"
              label-cols-lg="3"
              description="Target metric"
              label="Enter Metric"
              label-for="input-metric"
            >
              <b-form-textarea
                v-model="form.metric"
                id="input-metric"
                rows="3"
                max-rows="6"
                required
                @keydown.enter.exact.prevent
              ></b-form-textarea>
            </b-form-group>
          </b-col>
        </b-row>
        <b-row>
          <b-col>
            <b-form-group
              label-cols-sm="4"
              label-cols-lg="3"
              description="UTC Datetime"
              label="From"
              label-for="input-from-datetime"
            >
              <datetime
                v-model="form.fromDatetime"
                value-zone="UTC"
                id="input-from-datetime"
                type="datetime"
                required
              ></datetime>
            </b-form-group>
          </b-col>
          <b-col>
            <b-form-group
              label-cols-sm="4"
              label-cols-lg="3"
              description="UTC Datetime"
              label="To"
              label-for="input-to-datetime"
            >
              <datetime
                v-model="form.toDatetime"
                value-zone="UTC"
                id="input-to-datetime"
                type="datetime"
                required
              ></datetime>
            </b-form-group>
          </b-col>
        </b-row>
        <b-row>
          <b-col>
            <b-form-group
              label-cols-sm="4"
              label-cols-lg="3"
              description="second(s)"
              label="Window Size"
              label-for="input-window-size"
            >
              <b-form-input v-model="form.windowSize" id="input-window-size"></b-form-input>
            </b-form-group>
          </b-col>
          <b-col>
            <b-form-group
              label-cols-sm="4"
              label-cols-lg="3"
              description="second(s)"
              label="Offset Size"
              label-for="input-offset-size"
            >
              <b-form-input v-model="form.offsetSize" id="input-offset-size"></b-form-input>
            </b-form-group>
          </b-col>
          <b-col>
            <b-form-group
              label-cols-sm="4"
              label-cols-lg="3"
              description="second(s)"
              label="Sub-Window Size"
              label-for="input-sub-window-size"
            >
              <b-form-input v-model="form.subWindowSize" id="input-sub-window-size"></b-form-input>
            </b-form-group>
          </b-col>
          <b-col>
            <b-form-group
              label-cols-sm="4"
              label-cols-lg="3"
              description="second(s)"
              label="Alert Window Size"
              label-for="input-alert-window-size"
            >
              <b-form-input v-model="form.alertWindowSize" id="input-alert-window-size"></b-form-input>
            </b-form-group>
          </b-col>
        </b-row>
        <b-row align-h="around">
          <b-col md="2">
            <b-button block type="button" pill @click="fetchDatapoints">Fetch Metric</b-button>
          </b-col>
          <b-col md="2">
            <b-button block type="submit" pill>Fetch and Examine</b-button>
          </b-col>
          <b-col md="2">
            <b-button block type="reset" pill>Reset</b-button>
          </b-col>
        </b-row>
      </b-form>
      <div v-if="!loading">
        <highcharts v-if="series" :options="chartOptions"></highcharts>
      </div>
      <div v-else class="spinner">
        <div class="bounce1"></div>
        <div class="bounce2"></div>
        <div class="bounce3"></div>
      </div>
    </b-container>
  </div>
</template>

<script>
import { Chart } from "highcharts-vue";
import axios from "axios";
import moment from "moment";

export default {
  name: "Highcharts",
  components: {
    highcharts: Chart
  },
  data() {
    return {
      loading: false,
      form: {
        endpoint: "",
        metric: "",
        fromDatetime: "",
        toDatetime: "",
        windowSize: 0,
        offsetSize: 0,
        subWindowSize: 0,
        alertWindowSize: 0
      },
      xAxis: {},
      series: []
    };
  },
  computed: {
    chartOptions() {
      return {
        credits: { enabled: false },
        chart: { height: 500 },
        title: { text: "" },
        plotOptions: { line: { color: "#01579B" } },
        xAxis: this.xAxis,
        series: this.series
      };
    }
  },
  methods: {
    fetchDatapoints: function(e) {
      e.preventDefault();
      this.loading = true;
      axios
        .post("http://10.42.68.85:5001/api/fetch/compass", {
          endpoint: this.form.endpoint,
          metric: this.form.metric,
          fromDatetime: moment
            .utc(this.form.fromDatetime)
            .local()
            .format(),
          toDatetime: moment
            .utc(this.form.toDatetime)
            .local()
            .format()
        })
        .then(response => {
          const datapoints = response.data.datapoints;
          this.series = [
            {
              data: datapoints.data.map(([value]) => {
                return value;
              }),
              pointStart: datapoints.pointStart * 1000,
              pointInterval: datapoints.pointInterval * 1000,
              lineWidth: 1,
              states: { hover: { enabled: false } }
            }
          ];
          this.xAxis = {
            type: "datetime",
            dateTimeLabelFormats: {
              hour: "%b-%e %H:%M",
              day: "%b-%e %H",
              month: "%b-%e",
              year: "%y-%b-%e"
            }
          };
          this.loading = false;
        })
        .catch(() => {
          this.loading = false;
        });
    },
    onSubmit: function(e) {
      e.preventDefault();
      this.loading = true;
      axios
        .post("http://10.42.68.85:5001/api/examine/compass", {
          endpoint: this.form.endpoint,
          metric: this.form.metric,
          fromDatetime: moment
            .utc(this.form.fromDatetime)
            .local()
            .format(),
          toDatetime: moment
            .utc(this.form.toDatetime)
            .local()
            .format(),
          windowSize: this.form.windowSize,
          offsetSize: this.form.offsetSize,
          subWindowSize: this.form.subWindowSize,
          alertWindowSize: this.form.alertWindowSize
        })
        .then(response => {
          const datapoints = response.data.datapoints;
          const anomalies = response.data.anomalies.map(anomaly => {
            return {
              color: "rgba(255, 0, 0, 0.20",
              from: anomaly["from"] * 1000,
              to: anomaly["to"] * 1000
            };
          });
          this.series = [
            {
              data: datapoints.data.map(([value]) => {
                return value;
              }),
              pointStart: datapoints.pointStart * 1000,
              pointInterval: datapoints.pointInterval * 1000,
              lineWidth: 1,
              states: { hover: { enabled: false } }
            }
          ];
          this.xAxis = {
            type: "datetime",
            dateTimeLabelFormats: {
              hour: "%b-%e %H:%M",
              day: "%b-%e %H",
              month: "%b-%e",
              year: "%y-%b-%e"
            },
            plotBands: anomalies
          };
          this.loading = false;
        })
        .catch(() => {
          this.loading = false;
        });
    },
    onReset: function(e) {
      e.preventDefault();
    }
  }
};
</script>

<style scoped>
.spinner {
  margin: 100px auto 0;
  width: 70px;
  text-align: center;
}

.spinner > div {
  width: 18px;
  height: 18px;
  /* background-color: #333; */
  background-color: #01579b;

  border-radius: 100%;
  display: inline-block;
  -webkit-animation: sk-bouncedelay 1.4s infinite ease-in-out both;
  animation: sk-bouncedelay 1.4s infinite ease-in-out both;
}

.spinner .bounce1 {
  -webkit-animation-delay: -0.32s;
  animation-delay: -0.32s;
}

.spinner .bounce2 {
  -webkit-animation-delay: -0.16s;
  animation-delay: -0.16s;
}

@-webkit-keyframes sk-bouncedelay {
  0%,
  80%,
  100% {
    -webkit-transform: scale(0);
  }
  40% {
    -webkit-transform: scale(1);
  }
}

@keyframes sk-bouncedelay {
  0%,
  80%,
  100% {
    -webkit-transform: scale(0);
    transform: scale(0);
  }
  40% {
    -webkit-transform: scale(1);
    transform: scale(1);
  }
}
</style>
