import { Group, Header, Stack, Text } from "@mantine/core";
import Link from "next/link";
import React from "react";
import githubIcon from "../public/github-mark.svg";
import { useMediaQuery } from "@mantine/hooks";
import dbLogo from '../images/db-logo-black.svg';
import Image from 'next/image';
export enum MenuItem {
  Demo = "Demo",
  Playground = "Playground",
  About = "About",
}

const HeaderEvaluator = ({ activeTab }: { activeTab: MenuItem }) => {
  const mobileWidth = useMediaQuery("(max-width: 390px)");
  const borderBottom = "1px solid #000";

  return (
    <Header height={{ base: "75px" }}>
      <Stack justify="center" p="15px" pr={"25px"}>
        <Group position="apart">
          <Link href="/" style={{ textDecoration: "none" }}>
            <Group>
              {/* TODO(Kains) Ad proper image for displaying DB logo */}
              <Image src={dbLogo} alt='' width={30} height={30}/>
              {/* <Text size={mobileWidth === true ? "14px" : "28px"} color="#000">|🦜🔗</Text> */}
              <Text size={mobileWidth === true ? "14px" : "28px"} color="#000">| 🐞💫🦋</Text>
              <Text
                variant="gradient"
                gradient={{ from: "black", to: "#bf2015" }}
                size={mobileWidth === true ? "14px" : "28px"}
                weight="8em"
              >
                Interactive Evaluator
              </Text>
            </Group>
          </Link>
          <Group>
            <Link
              href="/"
              style={{
                textDecoration: "none",
                borderBottom: activeTab === MenuItem.Demo ? borderBottom : null,
              }}
            >
              <Text c="black">Demo</Text>
            </Link>
            <Link
              href="/playground"
              style={{
                textDecoration: "none",
                borderBottom:
                  activeTab === MenuItem.Playground ? borderBottom : null,
              }}
            >
              <Text c="black">Playground</Text>
            </Link>
            {/* <Link
              style={{ textDecoration: "none" }}
              href={
                "https://github.com/dankolesnikov/evaluator-app/blob/main/README.md"
              }
              target="_blank"
            >
              <Text c="black">Docs</Text>
            </Link> */}
            {/* <Link
              style={{
                textDecoration: "none",
                borderBottom:
                  activeTab === MenuItem.About ? borderBottom : null,
              }}
              href="/about"
            >
              <Text c="black">About</Text>
            </Link> */}
            {/* <Link
              href={"https://github.com/dankolesnikov/evaluator-app"}
              target="_blank"
            >
              <Image src={githubIcon} alt="github" width={30} height={30} />
            </Link> */}
          </Group>
        </Group>
      </Stack>
    </Header>
  );
};
export default HeaderEvaluator;
