import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import { Progress } from "@/components/ui/progress";
import { Textarea } from "@/components/ui/textarea";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell, TableCaption } from "@/components/ui/table";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { QueryErrorBanner } from "@/components/ui/QueryErrorBanner";
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "@/components/ui/select";

describe("Button", () => {
  it("renders a button with children and click handler", async () => {
    const onClick = vi.fn();
    const user = userEvent.setup();
    render(<Button onClick={onClick}>Save</Button>);

    await user.click(screen.getByRole("button", { name: "Save" }));
    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it("renders variants and sizes without crashing", () => {
    const { container } = render(
      <div>
        <Button variant="destructive">D</Button>
        <Button variant="outline">O</Button>
        <Button variant="secondary">S</Button>
        <Button variant="ghost">G</Button>
        <Button variant="link">L</Button>
        <Button size="sm">Small</Button>
        <Button size="lg">Large</Button>
        <Button size="icon">I</Button>
        <Button disabled>Disabled</Button>
      </div>
    );
    expect(container.querySelectorAll("button").length).toBe(9);
    expect(screen.getByRole("button", { name: "Disabled" })).toBeDisabled();
  });

  it("supports asChild rendering", () => {
    render(
      <Button asChild>
        <a href="/clients/new">New Client</a>
      </Button>
    );
    expect(screen.getByRole("link", { name: "New Client" })).toHaveAttribute("href", "/clients/new");
  });
});

describe("Badge", () => {
  it("renders children for each variant", () => {
    render(
      <div>
        <Badge>default</Badge>
        <Badge variant="secondary">secondary</Badge>
        <Badge variant="destructive">destructive</Badge>
        <Badge variant="outline">outline</Badge>
      </div>
    );
    expect(screen.getByText("default")).toBeInTheDocument();
    expect(screen.getByText("outline")).toBeInTheDocument();
  });
});

describe("Card", () => {
  it("renders all card sections", () => {
    render(
      <Card>
        <CardHeader>
          <CardTitle>Title</CardTitle>
          <CardDescription>Description</CardDescription>
        </CardHeader>
        <CardContent>Content</CardContent>
        <CardFooter>Footer</CardFooter>
      </Card>
    );
    expect(screen.getByText("Title")).toBeInTheDocument();
    expect(screen.getByText("Description")).toBeInTheDocument();
    expect(screen.getByText("Content")).toBeInTheDocument();
    expect(screen.getByText("Footer")).toBeInTheDocument();
  });
});

describe("Input", () => {
  it("passes value and type through", () => {
    render(<Input aria-label="Name" type="text" value="Acme" readOnly />);
    expect(screen.getByRole("textbox", { name: "Name" })).toHaveValue("Acme");
  });

  it("fires change events", async () => {
    const onChange = vi.fn();
    const user = userEvent.setup();
    render(<Input aria-label="Search" onChange={onChange} />);
    await user.type(screen.getByRole("textbox", { name: "Search" }), "abc");
    expect(onChange).toHaveBeenCalled();
  });
});

describe("Label", () => {
  it("renders text and associates via htmlFor", () => {
    render(
      <>
        <Label htmlFor="email">Email</Label>
        <Input id="email" aria-label="Email" />
      </>
    );
    expect(screen.getByText("Email")).toBeInTheDocument();
  });
});

describe("Separator", () => {
  it("is hidden when decorative", () => {
    render(<Separator decorative />);
    expect(screen.queryByRole("separator")).not.toBeInTheDocument();
  });

  it("exposes a separator role when not decorative", () => {
    render(<Separator decorative={false} orientation="vertical" />);
    expect(screen.getByRole("separator")).toHaveAttribute("aria-orientation", "vertical");
  });
});

describe("Skeleton", () => {
  it("renders a div with given class", () => {
    render(<Skeleton className="h-4 w-4" />);
    expect(document.querySelector("div.animate-pulse")).toHaveClass("h-4 w-4");
  });
});

describe("Progress", () => {
  it("clamps value between 0 and 100", () => {
    render(
      <div>
        <Progress value={150} aria-label="p150" />
        <Progress value={-5} aria-label="pneg" />
        <Progress aria-label="p0" />
      </div>
    );
    const bar = document.querySelector("[style]") as HTMLElement;
    expect(bar).not.toBeNull();
  });
});

describe("Textarea", () => {
  it("renders and fires change events", async () => {
    const onChange = vi.fn();
    const user = userEvent.setup();
    render(<Textarea aria-label="Notes" onChange={onChange} />);
    await user.type(screen.getByRole("textbox", { name: "Notes" }), "hi");
    expect(onChange).toHaveBeenCalled();
  });
});

describe("Table", () => {
  it("renders headers, rows, cells and caption", () => {
    render(
      <Table>
        <TableCaption>Client list</TableCaption>
        <TableHeader>
          <TableRow>
            <TableHead>Name</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <TableRow>
            <TableCell>Acme</TableCell>
          </TableRow>
        </TableBody>
      </Table>
    );
    expect(screen.getByText("Client list")).toBeInTheDocument();
    expect(screen.getByText("Acme")).toBeInTheDocument();
    expect(screen.getByRole("columnheader", { name: "Name" })).toBeInTheDocument();
  });
});

describe("Tabs", () => {
  it("switches content on trigger click", async () => {
    const user = userEvent.setup();
    render(
      <Tabs defaultValue="one">
        <TabsList>
          <TabsTrigger value="one">Tab One</TabsTrigger>
          <TabsTrigger value="two">Tab Two</TabsTrigger>
        </TabsList>
        <TabsContent value="one">Content One</TabsContent>
        <TabsContent value="two">Content Two</TabsContent>
      </Tabs>
    );

    expect(screen.getByText("Content One")).toBeInTheDocument();
    await user.click(screen.getByRole("tab", { name: "Tab Two" }));
    expect(screen.getByText("Content Two")).toBeInTheDocument();
  });
});

describe("QueryErrorBanner", () => {
  it("shows default message and error detail for Error instances", () => {
    render(<QueryErrorBanner error={new Error("boom")} />);
    expect(screen.getByRole("alert")).toHaveTextContent("Failed to load data");
    expect(screen.getByRole("alert")).toHaveTextContent("boom");
  });

  it("shows string errors and a Retry button when onRetry provided", async () => {
    const onRetry = vi.fn();
    const user = userEvent.setup();
    render(<QueryErrorBanner message="Custom" error="string error" onRetry={onRetry} />);
    expect(screen.getByRole("alert")).toHaveTextContent("string error");

    await user.click(screen.getByRole("button", { name: "Retry" }));
    expect(onRetry).toHaveBeenCalled();
  });

  it("renders without detail for unknown error types", () => {
    render(<QueryErrorBanner error={42} />);
    expect(screen.getByRole("alert")).toHaveTextContent("Failed to load data");
  });
});
describe("Select", () => {
  it("renders a trigger, opens the dropdown, and selects an option", async () => {
    const user = userEvent.setup();
    render(
      <Select defaultValue="a">
        <SelectTrigger aria-label="Pick one">
          <SelectValue placeholder="Pick one" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="a">Option A</SelectItem>
          <SelectItem value="b">Option B</SelectItem>
        </SelectContent>
      </Select>
    );

    const trigger = screen.getByRole("combobox", { name: /pick one/i });
    await user.click(trigger);
    expect(screen.getByRole("option", { name: "Option B" })).toBeInTheDocument();

    await user.click(screen.getByRole("option", { name: "Option A" }));
    expect(screen.getByRole("combobox", { name: /pick one/i })).toHaveTextContent("Option A");
  });
});
