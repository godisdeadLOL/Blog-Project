import { Box, Card, Container, For, HStack, Link, SimpleGrid, Stack, Text, VStack } from "@chakra-ui/react"
import { Provider } from "@/components/ui/provider"
import { Button } from "@/components/ui/button"
import { useEffect, useState } from "preact/hooks"
import { Avatar } from "./components/ui/avatar"

import { LuMessageCircle, LuShare2 } from "react-icons/lu"

const BoardInfo = ({}) => {
	return (
		<HStack>
			<Avatar variant="outline" name="lol lol"></Avatar>
			<Stack gap="0">
				<HStack>
					<Link fontWeight="medium">board_name</Link>
					<Text color="fg.subtle" textStyle="sm">
						&#x2022;
					</Text>
					<Text color="fg.subtle" textStyle="sm">
						5 минут назад
					</Text>
				</HStack>

				<Text color="fg.muted" textStyle="sm">
					<Link>user_name</Link>
				</Text>
			</Stack>
		</HStack>
	)
}

const BlogCard = ({}) => {
	return (
		<Card.Root variant="outline" px="4">
			<Card.Body gap="2">
				<BoardInfo />
				<Card.Title>Важность устойчивого потребления в современном мире.</Card.Title>
				<Card.Description as="div">
					<Text>
						В последние десятилетия тема устойчивого потребления стала одной из самых обсуждаемых в мире. Наши ресурсы не безграничны, и антропогенное воздействие на планету достигло критической
						точки. Отказ от бездумного потребления и переход к более устойчивым практикам может оказать значительное влияние на сохранение окружающей среды. Одним из ключевых аспектов устойчивого
						потребления является осознание каждого нашего шага, от покупки продуктов до использования ресурсов, таких как вода и энергия.
					</Text>
					<Text>
						Огромную роль играют бытовые привычки: использование многоразовых сумок, отказ от пластиковой упаковки и предпочтение местной продукции. Чем больше людей осознает важность этих изменений,
						тем быстрее удастся снизить нагрузку на экосистему.
					</Text>
				</Card.Description>
			</Card.Body>
			<Card.Footer>
				<Button variant="outline" size="sm">
					<LuMessageCircle />
					<Text color="fg.muted" textStyle="sm" as="div">
						151
					</Text>
				</Button>

				<Button variant="outline" size="sm">
					<LuShare2 />
				</Button>

				<Box flex={1}/>

				<Button variant="outline">Подробнее</Button>
			</Card.Footer>
		</Card.Root>
	)
}

export const App = ({}) => {
	const [posts, setPosts] = useState<any[]>([
		{
			title: "Название",
			content: "Текст",
		},
		{
			title: "Название",
			content: "Текст",
		},
	])

	// useEffect(() => {
	// 	fetch("http://127.0.0.1:5000/post")
	// 		.then((response) => response.json())
	// 		.then((data) => setPosts(data))
	// 		.catch((error) => console.error("Error fetching data:", error))
	// }, [])

	return (
		<Provider>
			<Container maxW="3xl">
				<Stack gap={4}>
					<For each={posts}>{(post) => <BlogCard />}</For>
				</Stack>
			</Container>
		</Provider>
	)
}
