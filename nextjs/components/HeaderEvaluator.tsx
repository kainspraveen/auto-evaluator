import { Group, Header, Stack, Text } from "@mantine/core";
import Link from "next/link";
import React from "react";
import githubIcon from "../public/github-mark.svg";
import { useMediaQuery } from "@mantine/hooks";
import dbLogo from '../images/db-logo-black.svg';
import Image from 'next/image';
export enum MenuItem {
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
              {/* <Image src={dbLogo} alt='' width={30} height={30}/> */}
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
              href="/playground"
              style={{
                textDecoration: "none",
                borderBottom:
                  activeTab === MenuItem.Playground ? borderBottom : null,
              }}
            >
              <Text c="black">Playground</Text>
            </Link>
            
            <Link
              style={{
                textDecoration: "none",
                borderBottom:
                  activeTab === MenuItem.About ? borderBottom : null,
              }}
              href="/about"
            >
              <Text c="black">About</Text>
            </Link>
            
          </Group>
        </Group>
      </Stack>
    </Header>
  );
};
export default HeaderEvaluator;
