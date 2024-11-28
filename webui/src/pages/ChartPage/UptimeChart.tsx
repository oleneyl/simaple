import { useWorkspace } from "@/hooks/useWorkspace";
import { getColorFromIndex } from "@/lib/chart";
import { secFormatter } from "@/lib/formatters.ts";
import { PlayLogResponse } from "@/sdk/models";
import ReactEChartsCore from "echarts-for-react/lib/core";
import { CustomChart, CustomSeriesOption } from "echarts/charts";
import {
  GridComponent,
  GridComponentOption,
  MarkLineComponent,
  MarkLineComponentOption,
  TooltipComponent,
  TooltipComponentOption,
} from "echarts/components";
import * as echarts from "echarts/core";
import { SVGRenderer } from "echarts/renderers";
import React, { useMemo } from "react";
import { Button } from "../../components/ui/button";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "../../components/ui/card";
import { Checkbox } from "../../components/ui/checkbox";
import { Label } from "../../components/ui/label";
import { useSkillData } from "@/hooks/useSkillData";

echarts.use([
  TooltipComponent,
  GridComponent,
  MarkLineComponent,
  CustomChart,
  SVGRenderer,
]);

type ECOption = echarts.ComposeOption<
  | CustomSeriesOption
  | TooltipComponentOption
  | GridComponentOption
  | MarkLineComponentOption
>;

export function useChart(
  history: PlayLogResponse[],
  skillNames: string[],
  trackingSkillNames: string[],
): ECOption {
  const { getIconPath } = useSkillData();

  const clock = history.length > 0 ? history[history.length - 1].clock : 0;

  function getUptimeSeries(history: PlayLogResponse[]) {
    const names = skillNames;
    const data = names.flatMap((name, i) => {
      return history
        .filter(
          (log) =>
            log.events.find(
              (event) => event.name === name && event.method === "use",
            ) && log.running_view[name].time_left > 0,
        )
        .map((log) => ({
          name,
          value: [
            i,
            log.clock,
            Math.min(log.clock + log.running_view[name].time_left, clock),
          ],
          itemStyle: {
            normal: {
              color: getColorFromIndex(i),
            },
          },
        }));
    });

    const trackingSkillClocks = trackingSkillNames.flatMap((name) =>
      history
        .filter((log) =>
          log.events.find(
            (event) => event.name === name && event.method === "use",
          ),
        )
        .map((log) => ({ name: name, clock: log.clock })),
    );

    return {
      data,
      renderItem: renderUptime,
      encode: {
        x: [1, 2],
        y: 0,
      },
      type: "custom",
      markLine: {
        silent: true,
        animation: true,
        animationDuration: 200,
        label: {
          show: false,
        },
        lineStyle: {
          type: "solid",
          color: "#bcbcbc",
        },
        data: [
          ...trackingSkillClocks.map(({ name, clock }) => ({
            symbol: `image://${getIconPath(name)}`,
            symbolSize: 24,
            symbolRotate: 0,
            xAxis: clock,
          })),
        ],
      },
    } satisfies CustomSeriesOption;
  }

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  function renderUptime(params: any, api: any) {
    const categoryIndex = api.value(0);
    const start = api.coord([api.value(1), categoryIndex]);
    const end = api.coord([api.value(2), categoryIndex]);
    const height = api.size([0, 1])[1] * 0.6;

    const rectShape = echarts.graphic.clipRectByRect(
      {
        x: start[0],
        y: start[1] - height / 2,
        width: end[0] - start[0],
        height: height,
      },
      {
        x: params.coordSys.x,
        y: params.coordSys.y,
        width: params.coordSys.width,
        height: params.coordSys.height,
      },
    );
    return (
      rectShape && {
        type: "rect" as const,
        transition: ["shape" as const],
        shape: rectShape,
        style: api.style(),
      }
    );
  }

  return {
    grid: {
      right: 32,
    },
    tooltip: {
      trigger: "item",
      formatter: (params) => {
        if (Array.isArray(params)) {
          throw new Error("Expected single value");
        }
        const values = params.value as [number, number, number];
        return `<span style="display:inline-block;margin-right:4px;border-radius:2px;width:10px;height:10px;background-color:${params.color};"></span><span class="font-mono font-medium tabular-nums text-xs text-foreground">${params.name}: ${secFormatter(values[1])} ~ ${secFormatter(values[2])}</span>`;
      },
      axisPointer: {
        type: "cross",
        animation: false,
      },
    },
    xAxis: {
      type: "value",
      min: 0,
      max: clock,
      axisLabel: {
        formatter: secFormatter,
      },
    },
    yAxis: [
      {
        type: "category",
        data: skillNames,
      },
    ],
    series: getUptimeSeries(history),
  };
}

const UptimeChart: React.FC = () => {
  const {
    history: logs,
    unfilteredHistory: unfilteredLogs,
    usedSkillNames,
  } = useWorkspace();
  const runningView = logs[0]?.running_view;
  const runningSkillNames = useMemo(
    () => (runningView ? Object.keys(runningView) : []),
    [runningView],
  );
  const usedRunningSkillNames = useMemo(
    () =>
      runningSkillNames.filter((name) =>
        unfilteredLogs.some((log) =>
          log.events.find(
            (event) => event.name === name && event.method === "use",
          ),
        ),
      ),
    [runningSkillNames, unfilteredLogs],
  );
  const [selectedRunningSkillNames, setSelectedRunningSkillNames] =
    React.useState<string[]>([]);
  const [trackingSkillNames, setTrackingSkillNames] = React.useState<string[]>(
    [],
  );

  const options = useChart(
    unfilteredLogs,
    selectedRunningSkillNames,
    trackingSkillNames,
  );

  return (
    <Card className="max-w-[1200px]">
      <CardHeader>
        <CardTitle>지속시간</CardTitle>
      </CardHeader>
      <CardContent>
        <ReactEChartsCore
          echarts={echarts}
          style={{ height: 500 }}
          option={options}
        />
      </CardContent>
      <CardFooter className="flex-col items-start gap-2 text-sm">
        <Label>스킬</Label>
        <div className="flex flex-wrap gap-4">
          {usedRunningSkillNames.map((skillName, i) => (
            <div key={skillName} className="flex gap-1 items-center">
              <Checkbox
                id={`runningView.skillNames.${i}`}
                key={skillName}
                checked={selectedRunningSkillNames.includes(skillName)}
                onCheckedChange={
                  selectedRunningSkillNames.includes(skillName)
                    ? () =>
                        setSelectedRunningSkillNames(
                          selectedRunningSkillNames.filter(
                            (name) => name !== skillName,
                          ),
                        )
                    : () =>
                        setSelectedRunningSkillNames([
                          ...selectedRunningSkillNames,
                          skillName,
                        ])
                }
              />
              <Label htmlFor={`runningView.skillNames.${i}`}>{skillName}</Label>
            </div>
          ))}
        </div>
        <div className="flex gap-2">
          <Button
            variant="secondary"
            size="sm"
            onClick={() => setSelectedRunningSkillNames(usedRunningSkillNames)}
          >
            전체 선택
          </Button>
          <Button
            variant="secondary"
            size="sm"
            onClick={() => setSelectedRunningSkillNames([])}
          >
            전체 해제
          </Button>
        </div>
        <Label>스킬</Label>
        <div className="flex flex-wrap gap-4">
          {usedSkillNames.map((skillName, i) => (
            <div key={skillName} className="flex gap-1 items-center">
              <Checkbox
                id={`tracking.skillNames.${i}`}
                key={skillName}
                checked={trackingSkillNames.includes(skillName)}
                onCheckedChange={
                  trackingSkillNames.includes(skillName)
                    ? () =>
                        setTrackingSkillNames(
                          trackingSkillNames.filter(
                            (name) => name !== skillName,
                          ),
                        )
                    : () =>
                        setTrackingSkillNames([
                          ...trackingSkillNames,
                          skillName,
                        ])
                }
              />
              <Label htmlFor={`tracking.skillNames.${i}`}>{skillName}</Label>
            </div>
          ))}
        </div>
      </CardFooter>
    </Card>
  );
};

export default UptimeChart;
